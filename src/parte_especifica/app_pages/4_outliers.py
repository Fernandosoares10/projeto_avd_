# [IA] Claude Code – pagina Outliers: multiplicador do IQR ajustavel, boxplot, tratamento (manter, limitar, remover) e relacao com o cancelamento
import pandas as pd
import plotly.express as px
import streamlit as st

from dados import (
    CLIENTE_CANCELOU,
    COLUNA_ALVO,
    CORES_SITUACAO,
    DICIONARIO_BANK,
    ORDEM_SITUACAO,
    ROTULOS_SITUACAO,
    carregar_bank,
)
from outliers import ESTRATEGIAS, K_IQR, mascara_outliers, resumo_outliers, taxa_alvo_por_grupo, tratar
from taxas import taxa_do_recorte, taxa_por_categoria

# Notas analiticas e titulo escritos pelo grupo (Fernando), iguais aos notebooks viz_exploratoria_4 e viz_explanatoria_2
TITULO_VIZ4 = 'Clientes com Menor Movimentação Apresentam Maior Taxa de Cancelamento'
NOTA_VIZ4_O_QUE_MOSTRA = 'O gráfico mostra a relação entre a quantidade de transações e o valor total que cada cliente movimentou em 12 meses. Cada ponto representa um cliente, e as cores diferenciam quem continuou no banco de quem cancelou.'
NOTA_VIZ4_INSIGHT = 'Existe uma relação positiva entre a quantidade de transações e o valor movimentado, com correlação de 0,81. Além disso, clientes que cancelaram costumam ter menos transações e movimentar menos dinheiro. O principal alerta está na região abaixo de 60 transações e US$ 3.000: ela concentra 34,9% dos clientes, mas reúne 77,9% de todos os cancelamentos. Isso indica que clientes com pouca movimentação merecem atenção do banco.'
NOTA_VIZ4_POR_QUE = 'Porque esse tipo de gráfico permite observar a relação entre duas variáveis numéricas ao mesmo tempo. Também facilita identificar concentrações de clientes, padrões, diferenças entre quem ficou e quem cancelou e possíveis grupos de maior risco. As linhas tracejadas ajudam a separar as regiões para a análise.'
NOTA_EXPL2_O_QUE_MOSTRA = 'O gráfico mostra a taxa de cancelamento dos clientes de acordo com a quantidade de produtos que possuem no banco, de 1 a 6. Também apresenta a quantidade de clientes em cada grupo e uma linha de referência com a taxa geral de cancelamento da base, que é de 16,1%.'
NOTA_EXPL2_INSIGHT = 'Clientes que possuem apenas 1 ou 2 produtos apresentam uma taxa de cancelamento maior, de 26,9%. Já entre os clientes que possuem de 4 a 6 produtos, a taxa cai para 11,4%. Ou seja, clientes com menos produtos cancelam aproximadamente 2,4 vezes mais. Outro ponto importante é que os clientes com 1 ou 2 produtos representam apenas 21,3% da base, mas correspondem a 35,6% de todos os cancelamentos. Isso mostra que ter poucos produtos contratados pode ser um sinal de maior risco de cancelamento.'
NOTA_EXPL2_POR_QUE = 'O gráfico de barras foi escolhido porque facilita comparar valores entre categorias diferentes, nesse caso, a quantidade de produtos contratados. Assim, fica fácil perceber quais grupos possuem as maiores e menores taxas de cancelamento. O vermelho foi usado para destacar os clientes com 1 ou 2 produtos, pois são os grupos que apresentam maior taxa de cancelamento e merecem mais atenção. A linha tracejada permite comparar cada grupo com a taxa geral da base.'


# Decisao do grupo sobre o tratamento (proposta do notebook eda_outliers.ipynb, para revisao)
TEXTO_DECISAO = """
1. **Manter todos os valores.** Os extremos sao plausiveis (clientes de renda alta, grandes gastadores, clientes
   mais velhos ou mais antigos) e nao ha erro de digitacao nem valor fora da escala.
2. **Nao remover linhas.** Tirar os outliers de todas as variaveis (com k = 1,5) descartaria 32,8% da base,
   justamente os perfis mais distintos. Os outliers tambem carregam informacao sobre o cancelamento.
3. **Limitar nas cercas do IQR so como recurso de analise**, em comparacoes sensiveis a escala (reduz a
   assimetria sem perder clientes).
4. **Variaveis de contagem** (contatos, meses inativo, meses de relacionamento): valores validos da escala.
"""

MIN_OUTLIERS_PARA_TAXA = 30

ROTULOS_ESTRATEGIA = {
    "manter": "Manter (nao altera nada)",
    "limitar": "Limitar (corta nas cercas do IQR)",
    "remover": "Remover (tira o cliente)",
}

df = carregar_bank()
colunas_numericas = df.select_dtypes(include="number").columns.drop("CLIENTNUM").tolist()


def rotulo(coluna: str) -> str:
    return f"{DICIONARIO_BANK[coluna][0]} ({coluna})"


def inteiro_br(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


st.caption(
    "Valores extremos das variaveis numericas: onde estao, se sao plausiveis, o que muda ao trata-los e se "
    "estao ligados ao cancelamento do cartao. Criterio: IQR (abaixo de Q1 - k x IQR ou acima de Q3 + k x IQR)."
)

k = st.slider(
    "Multiplicador do IQR (k)", min_value=1.0, max_value=3.0, value=K_IQR, step=0.5, key="out_k",
    help="1,5 e o criterio classico. Com k maior a cerca fica mais larga e sobram so os valores mais extremos.",
)

# ---------------------------------------------------------------- quantos outliers ha
@st.cache_data
def calcular_resumo(k_iqr: float) -> tuple[pd.DataFrame, pd.Series]:
    """Resumo por variavel e marca de 'tem algum outlier' por cliente, para um k (so recalcula se o k mudar)."""
    resumo_k = resumo_outliers(df, colunas_numericas, k=k_iqr)
    algum = pd.concat([mascara_outliers(df[c], "iqr", k=k_iqr) for c in colunas_numericas], axis=1).any(axis=1)
    return resumo_k, algum


resumo, algum_outlier = calcular_resumo(k)

with st.container(horizontal=True):
    st.metric("Clientes com pelo menos um outlier", inteiro_br(int(algum_outlier.sum())),
              f"{algum_outlier.mean() * 100:.1f}% da base", delta_color="off", border=True)
    st.metric("Variaveis com outliers", f"{int((resumo['total'] > 0).sum())} de {len(colunas_numericas)}",
              border=True)

with st.container(border=True):
    st.subheader("Quantos outliers ha em cada variavel", anchor=False)
    grafico = resumo.reset_index().sort_values("pct")
    fig_resumo = px.bar(
        grafico, x="pct", y="variavel", orientation="h", text=grafico["total"],
        title=f"Percentual de clientes fora das cercas do IQR (k = {k:g})",
        labels={"pct": "% de clientes da base", "variavel": ""},
        color_discrete_sequence=["#8DA0CB"],
    )
    fig_resumo.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_resumo, key="out_resumo")
    tabela = resumo.rename(columns={
        "limite_inferior": "Cerca inferior", "limite_superior": "Cerca superior", "abaixo": "Abaixo",
        "acima": "Acima", "total": "Total", "pct": "% da base", "total_z": "Total (z-score > 3)",
        "assimetria": "Assimetria",
    })
    st.dataframe(tabela.round(2).sort_values("Total", ascending=False),
                 alt="Outliers por variavel: cercas do IQR, quantidades, percentual e assimetria")
    st.caption("O z-score (|z| > 3) e mais rigoroso que o IQR em variaveis assimetricas: compare as duas colunas de total.")

# ---------------------------------------------------------------- uma variavel e o efeito do tratamento
with st.container(border=True):
    st.subheader("Uma variavel em detalhe e o efeito do tratamento", anchor=False)
    col_var, col_est = st.columns([3, 3], vertical_alignment="bottom")
    with col_var:
        var = st.selectbox("Variavel", colunas_numericas, index=colunas_numericas.index("Total_Trans_Amt"),
                           format_func=rotulo, key="out_var")
    with col_est:
        estrategia = st.radio("Tratamento", ESTRATEGIAS, format_func=ROTULOS_ESTRATEGIA.get, horizontal=True,
                              key="out_estrategia")

    tratado = tratar(df, [var], estrategia, k=k)
    taxa_original = (df[COLUNA_ALVO] == CLIENTE_CANCELOU).mean() * 100
    taxa_tratado = (tratado[COLUNA_ALVO] == CLIENTE_CANCELOU).mean() * 100

    if resumo.loc[var, "total"] == 0:
        st.info("Esta variavel nao tem outliers com o k escolhido: o tratamento nao muda nada.")

    with st.container(horizontal=True):
        st.metric("Clientes apos o tratamento", inteiro_br(len(tratado)), len(tratado) - len(df), border=True)
        st.metric("Media", f"{tratado[var].mean():,.2f}", round(tratado[var].mean() - df[var].mean(), 2),
                  delta_color="off", border=True)
        st.metric("Mediana", f"{tratado[var].median():,.2f}", round(tratado[var].median() - df[var].median(), 2),
                  delta_color="off", border=True)
        st.metric("Assimetria", f"{tratado[var].skew():.2f}", round(tratado[var].skew() - df[var].skew(), 2),
                  delta_color="off", border=True)
        st.metric("Taxa de cancelamento", f"{taxa_tratado:.1f}%", f"{taxa_tratado - taxa_original:+.1f} p.p.",
                  delta_color="off", border=True)

    comparacao = pd.concat([df.assign(Versao="Original"), tratado.assign(Versao=f"Tratado ({estrategia})")])
    fig_box = px.box(
        comparacao, x="Versao", y=var, color="Versao", points="outliers",
        title=f"{var}: original x tratado",
        labels={var: rotulo(var), "Versao": ""},
        color_discrete_sequence=["#8DA0CB", "#66C2A5"],
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, key="out_boxplot")

    outliers_var = df[mascara_outliers(df[var], "iqr", k=k)]
    with st.expander(f"Clientes outliers em {var} ({inteiro_br(len(outliers_var))})"):
        st.dataframe(outliers_var.drop(columns="CLIENTNUM"), hide_index=True,
                     alt=f"Clientes que sao outliers em {var}")
        st.download_button(":material/download: Baixar estes clientes (CSV)",
                           outliers_var.to_csv(index=False), file_name=f"outliers_{var}.csv", mime="text/csv",
                           key="out_download")

# ---------------------------------------------------------------- relacao com o cancelamento
with st.container(border=True):
    st.subheader("Ser outlier tem a ver com cancelar o cartao?", anchor=False)
    com_outliers = resumo.index[resumo["total"] > 0].tolist()
    if com_outliers:
        taxas = taxa_alvo_por_grupo(df, com_outliers, alvo=COLUNA_ALVO, positivo=CLIENTE_CANCELOU, k=k)
        # Taxa calculada sobre poucos clientes engana (0% de 2 clientes parece um efeito de -16 p.p.)
        taxas_confiaveis = taxas[taxas["n_outliers"] >= MIN_OUTLIERS_PARA_TAXA]
        poucos = taxas.index.difference(taxas_confiaveis.index).tolist()
        longo = (
            taxas_confiaveis.reset_index()
            .melt(id_vars="variavel", value_vars=["taxa_outliers", "taxa_demais"], var_name="Grupo", value_name="Taxa")
            .assign(Grupo=lambda d: d["Grupo"].map({"taxa_outliers": "Clientes outliers", "taxa_demais": "Demais clientes"}))
        )
        fig_taxa = px.bar(
            longo, x="Taxa", y="variavel", color="Grupo", barmode="group", orientation="h",
            color_discrete_map={"Clientes outliers": CORES_SITUACAO["Cancelou"], "Demais clientes": "#8C8C8C"},
            title="Taxa de cancelamento entre outliers e demais clientes",
            labels={"Taxa": "Taxa de cancelamento (%)", "variavel": ""},
        )
        st.plotly_chart(fig_taxa, key="out_cancelamento")
        st.caption(
            f"Taxa da base toda: {(df[COLUNA_ALVO] == CLIENTE_CANCELOU).mean() * 100:.1f}%. "
            "Barra vermelha maior que a cinza: quem e outlier cancela mais."
        )
        if poucos:
            st.caption(
                f"Fora do grafico por terem poucos outliers (menos de {MIN_OUTLIERS_PARA_TAXA} clientes, "
                f"taxa pouco confiavel): {', '.join(poucos)}."
            )
    else:
        st.info("Com este k nenhuma variavel tem outliers.")

# ---------------------------------------------------------------- decisao
with st.container(border=True):
    st.subheader("Decisao sobre o tratamento", anchor=False)
    st.markdown(TEXTO_DECISAO)
    st.caption("Proposta do notebook eda_outliers.ipynb, sujeita a revisao do grupo.")


def dec_br(valor: float, casas: int = 1) -> str:
    """Numero com virgula decimal para os textos corridos (as metricas seguem o padrao das outras paginas)."""
    return f"{valor:.{casas}f}".replace(".", ",")


# Cortes da visualizacao exploratoria 4: escolhidos olhando o grafico, so para descrever o que aparece nele
CORTE_TRANSACOES = 60
CORTE_VALOR_BAIXO = 3000
FAIXA_VALOR_MEDIO = (6000, 11000)
COLUNA_PRODUTOS = "Total_Relationship_Count"


@st.cache_data
def analisar_dispersao() -> dict:
    """Numeros e grafico da exploratoria 4. Nao dependem do k do slider, entao ficam em cache."""
    cancelou = df[COLUNA_ALVO] == CLIENTE_CANCELOU
    df_sit = df.assign(Situacao=df[COLUNA_ALVO].map(ROTULOS_SITUACAO))
    valor = df["Total_Trans_Amt"]
    canto = (df["Total_Trans_Ct"] < CORTE_TRANSACOES) & (valor < CORTE_VALOR_BAIXO)
    faixa_media = valor.between(*FAIXA_VALOR_MEDIO)
    faixa_intermediaria = (valor >= CORTE_VALOR_BAIXO) & (valor < FAIXA_VALOR_MEDIO[0])
    muito_alto = valor > FAIXA_VALOR_MEDIO[1]

    fig = px.scatter(
        df_sit, x="Total_Trans_Ct", y="Total_Trans_Amt", color="Situacao", opacity=0.35,
        category_orders={"Situacao": ORDEM_SITUACAO}, color_discrete_map=CORES_SITUACAO,
        title=TITULO_VIZ4,
        labels={"Total_Trans_Ct": "Quantidade de transacoes em 12 meses",
                "Total_Trans_Amt": "Valor total transacionado em 12 meses (US$)", "Situacao": "Situacao do cliente"},
    )
    fig.add_vline(x=CORTE_TRANSACOES, line_dash="dash", line_color="black")
    fig.add_hline(y=CORTE_VALOR_BAIXO, line_dash="dash", line_color="black")
    fig.update_layout(legend_title_text="Situacao do cliente")

    return {
        "fig": fig,
        "medianas": df_sit.groupby("Situacao")[["Total_Trans_Ct", "Total_Trans_Amt"]].median(),
        "correlacao": df["Total_Trans_Ct"].corr(valor),
        "taxa_base": cancelou.mean() * 100,
        "taxa_canto": taxa_do_recorte(df, canto, COLUNA_ALVO, CLIENTE_CANCELOU),
        "fatia_canto": canto[cancelou].mean() * 100,
        "canto_na_base": canto.mean() * 100,
        "taxa_faixa_media": taxa_do_recorte(df, faixa_media, COLUNA_ALVO, CLIENTE_CANCELOU),
        "fatia_faixa_media": faixa_media[cancelou].mean() * 100,
        "taxa_intermediaria": taxa_do_recorte(df, faixa_intermediaria, COLUNA_ALVO, CLIENTE_CANCELOU),
        "cancelaram_muito_alto": int(cancelou[muito_alto].sum()),
        "n_muito_alto": int(muito_alto.sum()),
    }


@st.cache_data
def analisar_produtos() -> dict:
    """Numeros e grafico da explanatoria 2. Nao dependem do k do slider, entao ficam em cache."""
    cancelou = df[COLUNA_ALVO] == CLIENTE_CANCELOU
    por_produtos = taxa_por_categoria(df, COLUNA_PRODUTOS, COLUNA_ALVO, CLIENTE_CANCELOU)
    poucos = df[COLUNA_PRODUTOS] <= 2
    muitos = df[COLUNA_PRODUTOS] >= 4
    taxa_base = cancelou.mean() * 100
    taxa_poucos = taxa_do_recorte(df, poucos, COLUNA_ALVO, CLIENTE_CANCELOU)
    taxa_muitos = taxa_do_recorte(df, muitos, COLUNA_ALVO, CLIENTE_CANCELOU)
    razao = taxa_poucos / taxa_muitos

    grafico = por_produtos.reset_index().assign(
        Rotulo=lambda d: d[COLUNA_PRODUTOS].astype(int).astype(str) + " (n = " + d["n"].map(inteiro_br) + ")",
        Grupo=lambda d: d[COLUNA_PRODUTOS].map(lambda p: "1 ou 2 produtos" if p <= 2 else "3 ou mais produtos"),
    )
    fig = px.bar(
        grafico, x="Rotulo", y="taxa", color="Grupo", text=grafico["taxa"].map(lambda t: f"{t:.1f}%"),
        color_discrete_map={"1 ou 2 produtos": CORES_SITUACAO["Cancelou"], "3 ou mais produtos": "#8C8C8C"},
        title=f"Clientes com 1 ou 2 produtos tem taxa de cancelamento {dec_br(razao)} vezes a dos clientes com 4 a 6",
        labels={"Rotulo": "Numero de produtos do banco que o cliente tem", "taxa": "Taxa de cancelamento (%)", "Grupo": ""},
    )
    fig.add_hline(y=taxa_base, line_dash="dash", line_color="black",
                  annotation_text=f"Base toda: {dec_br(taxa_base)}%", annotation_position="top right")
    fig.update_traces(textposition="outside", cliponaxis=False)

    return {
        "fig": fig,
        "taxa_poucos": taxa_poucos,
        "taxa_muitos": taxa_muitos,
        "taxa_tres": por_produtos.loc[3, "taxa"],
        "razao": razao,
        "poucos_na_base": poucos.mean() * 100,
        "poucos_nos_cancelados": poucos[cancelou].mean() * 100,
    }


def secao_dispersao() -> None:
    d = analisar_dispersao()
    med = d["medianas"]
    st.subheader("Visualizacao exploratoria 4: transacoes x valor transacionado", anchor=False)
    with st.container(horizontal=True):
        st.metric("Mediana de transacoes: ficou", f"{med.loc['Ficou', 'Total_Trans_Ct']:.0f}", border=True)
        st.metric("Mediana de transacoes: cancelou", f"{med.loc['Cancelou', 'Total_Trans_Ct']:.0f}", border=True)
        st.metric("Mediana do valor (US$): ficou", f"{med.loc['Ficou', 'Total_Trans_Amt']:,.0f}", border=True)
        st.metric("Mediana do valor (US$): cancelou", f"{med.loc['Cancelou', 'Total_Trans_Amt']:,.0f}", border=True)
    st.plotly_chart(d["fig"], key="out_viz4")
    st.caption("Cada ponto e um cliente; a transparencia ajuda a ler onde os pontos se sobrepoem. "
               "As linhas tracejadas marcam 60 transacoes e US$ 3.000.")

    with st.expander("Nota analitica", icon=":material/edit_note:"):
        st.markdown(f"**O que esta sendo mostrado:** {NOTA_VIZ4_O_QUE_MOSTRA}")
        st.markdown(f"**Qual insight pode ser extraido:** {NOTA_VIZ4_INSIGHT}")
        st.markdown(f"**Por que este tipo de visualizacao:** {NOTA_VIZ4_POR_QUE}")

def secao_produtos() -> None:
    d = analisar_produtos()
    st.subheader("Visualizacao explanatoria 2: produtos do banco e cancelamento", anchor=False)
    with st.container(horizontal=True):
        st.metric("Cancelam com 1 ou 2 produtos", f"{d['taxa_poucos']:.1f}%", border=True)
        st.metric("Cancelam com 4 a 6 produtos", f"{d['taxa_muitos']:.1f}%", border=True)
        st.metric("Diferenca entre os dois grupos", f"{d['razao']:.1f}x", border=True)
    st.plotly_chart(d["fig"], key="out_expl2")
    with st.expander("Nota analitica", icon=":material/edit_note:"):
        st.markdown(f"**O que esta sendo mostrado:** {NOTA_EXPL2_O_QUE_MOSTRA}")
        st.markdown(f"**Qual insight pode ser extraido:** {NOTA_EXPL2_INSIGHT}")
        st.markdown(f"**Por que este tipo de visualizacao:** {NOTA_EXPL2_POR_QUE}")

with st.container(border=True):
    secao_dispersao()

with st.container(border=True):
    secao_produtos()
