# [IA] Claude Code – pagina Outliers: multiplicador do IQR ajustavel, boxplot, tratamento (manter, limitar, remover) e relacao com o cancelamento
import pandas as pd
import plotly.express as px
import streamlit as st

from dados import (
    CLIENTE_CANCELOU,
    COLUNA_ALVO,
    CORES_SITUACAO,
    DICIONARIO_BANK,
    carregar_bank,
)
from outliers import ESTRATEGIAS, K_IQR, mascara_outliers, resumo_outliers, taxa_alvo_por_grupo, tratar

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
