# [IA] Claude Code – pagina Distribuicoes: filtros interligados, histograma, violino e barras das categoricas
import pandas as pd
import plotly.express as px
import streamlit as st

from dados import (
    COLUNA_ALVO,
    CORES_SITUACAO,
    DICIONARIO_BANK,
    ORDEM_CATEGORIAS,
    ORDEM_SITUACAO,
    ROTULOS_SITUACAO,
    carregar_bank,
)

# Nota analitica da visualizacao exploratoria 2 (texto do grupo, adaptado do notebook)
NOTA_VIZ2_O_QUE_MOSTRA = "O gráfico mostra a variável `Total_Trans_Ct`, que representa a quantidade de transações em 12 meses, comparando os grupos `Ficou` e `Cancelou`, derivados de `Attrition_Flag`. A largura do violino representa a densidade dos valores, ou seja, onde há maior concentração de clientes. A caixa dentro de cada violino mostra o primeiro quartil (Q1), a mediana e o terceiro quartil (Q3)."
NOTA_VIZ2_INSIGHT = "Na base completa, sem filtros, a mediana de quem cancelou é 43 transações, enquanto a de quem ficou é 71. Portanto, a mediana de quem cancelou fica 28 transações abaixo da mediana de quem ficou. Os dois picos aparecem no grupo `Ficou`, sugerindo uma distribuição bimodal e a existência de dois perfis de clientes ativos, com níveis de uso distintos; os clientes que cancelaram estão mais concentrados em uma faixa mais baixa de transações."
NOTA_VIZ2_POR_QUE = "O violino foi escolhido em vez do boxplot porque, além de mostrar os quartis, a mediana e a comparação entre os grupos, evidencia a forma da distribuição e torna visíveis os dois picos da distribuição bimodal observada em `Total_Trans_Ct`."

df = carregar_bank().assign(Situacao=lambda d: d[COLUNA_ALVO].map(ROTULOS_SITUACAO))
colunas_numericas = df.select_dtypes(include="number").columns.drop("CLIENTNUM").tolist()
colunas_categoricas = ["Gender", "Education_Level", "Marital_Status", "Income_Category", "Card_Category"]


def ordem(coluna: str) -> list[str]:
    """Categorias na ordem natural (ordinais) ou por frequencia (nominais)."""
    return ORDEM_CATEGORIAS.get(coluna, df[coluna].value_counts().index.tolist())


def rotulo(coluna: str) -> str:
    return f"{DICIONARIO_BANK[coluna][0]} ({coluna})"


st.caption("Como cada variavel se distribui. Os filtros da barra lateral valem para todos os graficos da pagina.")

# ---------------------------------------------------------------- filtros (barra lateral)
with st.sidebar:
    st.header("Filtros", anchor=False)
    f_situacao = st.pills("Situacao do cliente", ORDEM_SITUACAO, selection_mode="multi",
                          default=ORDEM_SITUACAO, key="dist_situacao")
    f_genero = st.pills("Genero", ordem("Gender"), selection_mode="multi",
                        default=ordem("Gender"), key="dist_genero")
    f_idade = st.slider("Idade", int(df["Customer_Age"].min()), int(df["Customer_Age"].max()),
                        (int(df["Customer_Age"].min()), int(df["Customer_Age"].max())), key="dist_idade")
    f_renda = st.multiselect("Faixa de renda", ordem("Income_Category"),
                             default=ordem("Income_Category"), key="dist_renda")
    f_cartao = st.pills("Categoria do cartao", ordem("Card_Category"), selection_mode="multi",
                        default=ordem("Card_Category"), key="dist_cartao")
    f_escolaridade = st.multiselect("Escolaridade", ordem("Education_Level"),
                                    default=ordem("Education_Level"), key="dist_escolaridade")
    f_estado_civil = st.multiselect("Estado civil", ordem("Marital_Status"),
                                    default=ordem("Marital_Status"), key="dist_estado_civil")

filtrado = df[
    df["Situacao"].isin(f_situacao)
    & df["Gender"].isin(f_genero)
    & df["Customer_Age"].between(*f_idade)
    & df["Income_Category"].isin(f_renda)
    & df["Card_Category"].isin(f_cartao)
    & df["Education_Level"].isin(f_escolaridade)
    & df["Marital_Status"].isin(f_estado_civil)
]

# ---------------------------------------------------------------- resumo do recorte
taxa_geral = (df["Situacao"] == "Cancelou").mean() * 100
taxa_recorte = (filtrado["Situacao"] == "Cancelou").mean() * 100 if len(filtrado) else 0.0
with st.container(horizontal=True):
    st.metric("Clientes no recorte", f"{len(filtrado):,}".replace(",", "."),
              f"{len(filtrado) / len(df) * 100:.1f}% da base", delta_color="off", border=True)
    diferenca = round(taxa_recorte - taxa_geral, 1)
    # Delta numerico 0 fica cinza e sem seta; texto "+0.0" seria pintado como aumento
    st.metric("Taxa de cancelamento no recorte", f"{taxa_recorte:.1f}%",
              f"{diferenca:+.1f} p.p. vs. base toda" if diferenca else 0,
              delta_description="vs. base toda" if not diferenca else None,
              delta_color="inverse", border=True)

if filtrado.empty:
    st.warning("Nenhum cliente atende aos filtros. Amplie a selecao na barra lateral.", title="Recorte vazio")
    st.stop()

st.download_button(":material/download: Baixar o recorte (CSV)", filtrado.drop(columns="Situacao").to_csv(index=False),
                   file_name="bankchurners_recorte.csv", mime="text/csv")

# ---------------------------------------------------------------- variaveis numericas
with st.container(border=True):
    st.subheader("Variaveis numericas", anchor=False)
    col_var, col_sep = st.columns([3, 2], vertical_alignment="bottom")
    with col_var:
        var_num = st.selectbox("Variavel", colunas_numericas, index=colunas_numericas.index("Total_Trans_Ct"),
                               format_func=rotulo, key="dist_var_num")
    with col_sep:
        separar = st.toggle("Separar por situacao do cliente", value=True, key="dist_separar")

    # Grupos com tamanhos muito diferentes (8.500 x 1.627): com separacao, o eixo y vira % do proprio grupo
    fig_hist = px.histogram(
        filtrado, x=var_num, nbins=40,
        color="Situacao" if separar else None,
        category_orders={"Situacao": ORDEM_SITUACAO},
        color_discrete_map=CORES_SITUACAO,
        color_discrete_sequence=["#4C72B0"],
        barmode="overlay", opacity=0.65 if separar else 0.9,
        histnorm="percent" if separar else None,
        title=f"Distribuicao de {var_num}" + (" por situacao do cliente" if separar else ""),
        labels={var_num: rotulo(var_num), "Situacao": "Situacao do cliente"},
    )
    fig_hist.update_layout(yaxis_title="% de clientes do grupo" if separar else "Quantidade de clientes",
                           legend_title_text="Situacao do cliente", bargap=0.02)
    st.plotly_chart(fig_hist, key="dist_hist")
    if separar:
        st.caption("Com a separacao ligada, cada cor soma 100%: assim grupos de tamanhos diferentes ficam comparaveis.")

    grupos = filtrado.groupby("Situacao")[var_num] if separar else filtrado.assign(Situacao="Todos").groupby("Situacao")[var_num]
    resumo = grupos.describe()[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    resumo["assimetria"] = grupos.skew()
    resumo = resumo.reindex([g for g in ORDEM_SITUACAO + ["Todos"] if g in resumo.index])
    resumo.columns = ["Clientes", "Media", "Desvio padrao", "Minimo", "Q1", "Mediana", "Q3", "Maximo", "Assimetria"]
    st.dataframe(resumo.round(2), alt=f"Medidas resumo de {var_num}")

# ---------------------------------------------------------------- visualizacao exploratoria 2 (escolha do Luis)
with st.container(border=True):
    st.subheader("Visualizacao exploratoria 2: transacoes de quem ficou x quem cancelou", anchor=False)
    fig_violino = px.violin(
        filtrado, x="Situacao", y="Total_Trans_Ct", color="Situacao",
        category_orders={"Situacao": ORDEM_SITUACAO}, color_discrete_map=CORES_SITUACAO,
        box=True, points=False,
        title="Quantidade de transacoes em 12 meses: clientes que ficaram x clientes que cancelaram",
        labels={"Situacao": "Situacao do cliente", "Total_Trans_Ct": "Quantidade de transacoes em 12 meses"},
    )
    fig_violino.update_traces(spanmode="hard")  # nao estende a densidade alem dos valores observados
    fig_violino.update_layout(legend_title_text="Situacao do cliente")
    st.plotly_chart(fig_violino, key="dist_violino")
    qtd = filtrado["Situacao"].value_counts()
    st.caption(
        "A caixa dentro de cada violino marca Q1, mediana e Q3. Os violinos tem a mesma area, entao a largura "
        "nao indica a quantidade de clientes: "
        + " | ".join(f"{s}: n = {qtd.get(s, 0):,}".replace(",", ".") for s in ORDEM_SITUACAO)
    )
    with st.expander("Nota analitica", icon=":material/edit_note:"):
        st.markdown(f"**O que esta sendo mostrado:** {NOTA_VIZ2_O_QUE_MOSTRA}")
        st.markdown(f"**Qual insight pode ser extraido:** {NOTA_VIZ2_INSIGHT}")
        st.markdown(f"**Por que este tipo de visualizacao:** {NOTA_VIZ2_POR_QUE}")

# ---------------------------------------------------------------- variaveis categoricas
with st.container(border=True):
    st.subheader("Variaveis categoricas", anchor=False)
    col_cat, col_modo = st.columns([3, 2], vertical_alignment="bottom")
    with col_cat:
        var_cat = st.selectbox("Variavel", colunas_categoricas, format_func=rotulo, key="dist_var_cat")
    with col_modo:
        modo = st.segmented_control("Mostrar", ["Quantidade", "% do recorte"], default="Quantidade",
                                    key="dist_modo_cat")

    contagem = (
        filtrado[var_cat].value_counts().reindex(ordem(var_cat)).fillna(0).astype(int)
        .rename_axis(var_cat).reset_index(name="Quantidade")
    )
    contagem["% do recorte"] = (contagem["Quantidade"] / contagem["Quantidade"].sum() * 100).round(1)
    medida = modo or "Quantidade"
    contagem["Destaque"] = contagem[var_cat].eq("Unknown").map({True: "Unknown (ausente)", False: "Valor informado"})
    fig_bar = px.bar(
        contagem, y=var_cat, x=medida, orientation="h", text=medida, color="Destaque",
        color_discrete_map={"Valor informado": "#4C72B0", "Unknown (ausente)": "#B0B0B0"},
        category_orders={var_cat: ordem(var_cat)},
        title=f"Distribuicao de {var_cat}",
        labels={var_cat: rotulo(var_cat), medida: "Quantidade de clientes" if medida == "Quantidade" else "% de clientes do recorte"},
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}%" if medida != "Quantidade" else "%{text}", textposition="outside",
                          cliponaxis=False)
    fig_bar.update_layout(legend_title_text="")
    st.plotly_chart(fig_bar, key="dist_barras")
