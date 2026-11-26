# [IA] Claude Code – pagina Qualidade dos dados: estrutura da base, valores Unknown, tratamento e visualizacao exploratoria 1
import pandas as pd
import plotly.express as px
import streamlit as st

from dados import (
    COLUNA_ALVO,
    CORES_SITUACAO,
    DICIONARIO_BANK,
    ORDEM_SITUACAO,
    ROTULOS_SITUACAO,
    carregar_bank,
)

COLUNAS_COM_UNKNOWN = ["Education_Level", "Marital_Status", "Income_Category"]

# Textos definidos pelo grupo em eda_unknown.ipynb (a IA nao escreve o mecanismo nem a justificativa)
TRATAMENTO_ESCOLHIDO = "Unknown mantido como categoria propria (nenhuma linha removida, nenhum valor inventado)"
MECANISMO_DE_AUSENCIA = 'Para Education_Level, o mecanismo mais próximo parece ser MCAR, pois as taxas de Unknown apresentam poucas diferenças entre os grupos analisados. Para Marital_Status, existem algumas diferenças conforme outras variáveis, então podemos considerar a possibilidade de MAR. Já em Income_Category, a ausência apresenta uma diferença muito grande entre homens e mulheres, indicando um comportamento mais próximo de MAR. Não é possível afirmar esses mecanismos com certeza apenas pelas tabelas, principalmente porque não conseguimos observar diretamente o motivo pelo qual cada cliente deixou de informar seus dados.'
JUSTIFICATIVA_TRATAMENTO = 'Decidimos manter Unknown como uma categoria própria porque não sabemos qual seria o valor correto de cada informação ausente. Substituir pela moda poderia criar informações que não correspondem à realidade dos clientes. Além disso, manter essa categoria permite analisar os registros sem excluir clientes ou perder informações importantes.'

# Nota analitica da visualizacao exploratoria 1 (texto do grupo, igual ao notebook viz_exploratoria_1.ipynb)
NOTA_VIZ1_O_QUE_MOSTRA = "O gráfico apresenta uma comparação da distribuição do valor total de transações realizadas pelos clientes nos últimos 12 meses (Total_Trans_Amt), separando aqueles que permaneceram no banco daqueles que cancelaram o cartão (Attrition_Flag). São apresentados a mediana, os quartis, a dispersão dos valores e possíveis pontos discrepantes de cada grupo."
NOTA_VIZ1_INSIGHT = "É possível observar que os clientes que permaneceram no banco apresentam uma mediana de transações de US$ 4.100, enquanto os clientes que cancelaram possuem uma mediana de US$ 2.329. Essa diferença indica que os clientes que cancelaram o cartão apresentavam, em geral, menor volume de transações financeiras. Isso sugere uma associação entre menor utilização do cartão e maior ocorrência de cancelamentos."
NOTA_VIZ1_POR_QUE = "Foi escolhido o gráfico de boxplot utilizando as variáveis Total_Trans_Amt e Attrition_Flag. Essa visualização permite comparar a distribuição dos valores totais de transações entre clientes que permaneceram no banco e clientes que cancelaram o cartão. A escolha se justifica pela facilidade de visualizar as medianas, a dispersão e possíveis valores discrepantes, permitindo identificar diferenças no comportamento financeiro dos dois grupos."


def formatar_int(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


df = carregar_bank()
eh_unknown = df[COLUNAS_COM_UNKNOWN].eq("Unknown")
linhas_com_unknown = eh_unknown.any(axis=1)

st.caption("Estrutura da base, valores ausentes registrados como \"Unknown\" e o tratamento adotado.")

# ---------------------------------------------------------------- numeros gerais da qualidade
with st.container(horizontal=True):
    st.metric("Linhas", formatar_int(len(df)), border=True)
    st.metric("Colunas", f"{df.shape[1]}", border=True, help="Inclui o identificador CLIENTNUM.")
    st.metric("Valores NaN", formatar_int(int(df.isna().sum().sum())), border=True)
    st.metric("Linhas duplicadas", formatar_int(int(df.duplicated().sum())), border=True)
    st.metric("Linhas com Unknown", f"{linhas_com_unknown.mean() * 100:.1f}%", border=True,
              help=f"{formatar_int(int(linhas_com_unknown.sum()))} linhas com pelo menos um Unknown.")

# ---------------------------------------------------------------- estrutura da base
with st.container(border=True):
    st.subheader(":material/table_chart: Estrutura da base", anchor=False)

    estrutura = pd.DataFrame({
        "Coluna": df.columns,
        "Significado": [DICIONARIO_BANK[c][0] for c in df.columns],
        "Tipo estatistico": [DICIONARIO_BANK[c][1] for c in df.columns],
        "dtype (pandas)": df.dtypes.astype(str).values,
        "Valores distintos": df.nunique().values,
        "NaN": df.isna().sum().values,
        "Unknown": [int((df[c] == "Unknown").sum()) for c in df.columns],
    })
    estrutura["Grupo"] = ["Numerica" if pd.api.types.is_numeric_dtype(df[c]) else "Categorica" for c in df.columns]

    grupo = st.segmented_control("Mostrar", ["Todas", "Numerica", "Categorica"], default="Todas",
                                 key="qual_grupo")
    if grupo in ("Numerica", "Categorica"):
        estrutura = estrutura[estrutura["Grupo"] == grupo]
    st.dataframe(estrutura.drop(columns="Grupo"), hide_index=True,
                 alt="Tabela com o tipo, valores distintos, NaN e Unknown de cada coluna")

# ---------------------------------------------------------------- valores Unknown
with st.container(border=True):
    st.subheader(":material/help_center: Valores Unknown", anchor=False)
    st.caption("No BankChurners a ausencia nao aparece como NaN: ela foi registrada como o texto \"Unknown\".")

    with st.container(horizontal=True):
        for coluna in COLUNAS_COM_UNKNOWN:
            qtd = int(eh_unknown[coluna].sum())
            st.metric(f"Unknown em {coluna}", f"{qtd / len(df) * 100:.1f}%", border=True,
                      help=f"{formatar_int(qtd)} clientes.")

    st.markdown("**Taxa de Unknown (%) por grupo**")
    variavel_grupo = st.selectbox(
        "Separar por", ["Attrition_Flag", "Gender", "Card_Category"],
        format_func=lambda c: f"{DICIONARIO_BANK[c][0]} ({c})", key="qual_unknown_por",
    )
    taxa = (
        pd.concat([df[variavel_grupo], eh_unknown], axis=1)
        .groupby(variavel_grupo)[COLUNAS_COM_UNKNOWN].mean()
        .mul(100).round(2)
    )
    taxa.columns = [f"% Unknown em {c}" for c in taxa.columns]
    taxa["Clientes"] = df[variavel_grupo].value_counts()
    st.dataframe(taxa, alt=f"Porcentagem de Unknown em cada coluna, por {variavel_grupo}")

    st.markdown("**Combinacoes de Unknown nas tres colunas**")
    combinacoes = (
        eh_unknown.value_counts()
        .rename("Linhas")
        .reset_index()
        .replace({True: "Unknown", False: "informado"})
    )
    st.dataframe(combinacoes, hide_index=True, alt="Quantidade de linhas para cada combinacao de Unknown")

# ---------------------------------------------------------------- mecanismo e tratamento
with st.container(border=True):
    st.subheader(":material/build: Mecanismo de ausencia e tratamento", anchor=False)
    st.markdown(f"**Tratamento adotado:** {TRATAMENTO_ESCOLHIDO}")
    st.markdown(f"**Mecanismo de ausencia:** {MECANISMO_DE_AUSENCIA}")
    st.markdown(f"**Justificativa:** {JUSTIFICATIVA_TRATAMENTO}")
    st.caption("Detalhes e tabelas completas em src/parte_especifica/eda_unknown.ipynb.")

# ---------------------------------------------------------------- visualizacao exploratoria 1 (escolha do Fernando)
with st.container(border=True):
    st.subheader("Visualizacao exploratoria 1: valor transacionado de quem ficou x quem cancelou", anchor=False)

    dados_viz = df.assign(Situacao=df[COLUNA_ALVO].map(ROTULOS_SITUACAO))
    mostrar_discrepantes = st.toggle("Mostrar valores discrepantes", value=True, key="qual_discrepantes")

    fig_box = px.box(
        dados_viz, x="Situacao", y="Total_Trans_Amt", color="Situacao",
        category_orders={"Situacao": ORDEM_SITUACAO}, color_discrete_map=CORES_SITUACAO,
        points="outliers" if mostrar_discrepantes else False,
        title="Valor total transacionado em 12 meses: clientes que ficaram x clientes que cancelaram",
        labels={"Situacao": "Situacao do cliente", "Total_Trans_Amt": "Valor total transacionado em 12 meses (US$)"},
    )
    fig_box.update_layout(legend_title_text="Situacao do cliente")
    st.plotly_chart(fig_box, key="qual_boxplot")

    resumo = dados_viz.groupby("Situacao")["Total_Trans_Amt"].describe().reindex(ORDEM_SITUACAO)
    resumo = resumo[["count", "min", "25%", "50%", "75%", "max"]]
    resumo.columns = ["Clientes", "Minimo", "Q1", "Mediana", "Q3", "Maximo"]
    st.dataframe(resumo.round(1), alt="Quartis de Total_Trans_Amt por situacao do cliente")
    st.caption("Os pontos isolados sao valores alem de 1,5 x IQR a partir da caixa (valores discrepantes).")

    with st.expander("Nota analitica", icon=":material/edit_note:"):
        st.markdown(f"**O que esta sendo mostrado:** {NOTA_VIZ1_O_QUE_MOSTRA}")
        st.markdown(f"**Qual insight pode ser extraido:** {NOTA_VIZ1_INSIGHT}")
        st.markdown(f"**Por que este tipo de visualizacao:** {NOTA_VIZ1_POR_QUE}")
