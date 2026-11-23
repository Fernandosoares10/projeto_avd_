# [IA] Claude Code – pagina inicial: contexto, pergunta de pesquisa, publico-alvo e numeros gerais
import pandas as pd
import streamlit as st

from dados import CLIENTE_CANCELOU, COLUNA_ALVO, DICIONARIO_BANK, carregar_bank

# Textos definidos pelo grupo (a IA nao escreve pergunta de pesquisa nem publico-alvo)
PERGUNTA_DE_PESQUISA = "_(texto do grupo)_"
PUBLICO_ALVO = "_(texto do grupo)_"

df = carregar_bank()
cancelou = df[COLUNA_ALVO] == CLIENTE_CANCELOU

st.caption(
    "Credit Card Customers (BankChurners), Kaggle. "
    "Clientes de cartao de credito de um banco e quem cancelou o cartao."
)

# Numeros gerais da base
with st.container(horizontal=True):
    st.metric("Clientes na base", f"{len(df):,}".replace(",", "."), border=True)
    st.metric("Cancelaram o cartao", f"{cancelou.sum():,}".replace(",", "."), border=True)
    st.metric("Taxa de cancelamento", f"{cancelou.mean() * 100:.1f}%", border=True)
    st.metric("Variaveis", f"{df.shape[1] - 1}", border=True,
              help="Sem contar o identificador CLIENTNUM.")

col_pergunta, col_publico = st.columns(2)
with col_pergunta:
    with st.container(border=True, height="stretch"):
        st.subheader(":material/help: Pergunta de pesquisa", anchor=False)
        st.markdown(PERGUNTA_DE_PESQUISA)
with col_publico:
    with st.container(border=True, height="stretch"):
        st.subheader(":material/groups: Publico-alvo", anchor=False)
        st.markdown(PUBLICO_ALVO)

with st.container(border=True):
    st.subheader(":material/map: Como navegar", anchor=False)
    st.markdown(
        "- **Qualidade dos dados**: estrutura da base e tratamento dos valores Unknown.\n"
        "- **Distribuicoes**: como cada variavel se distribui, com filtros por perfil.\n"
        "- **Relacoes**: o que muda entre quem ficou e quem cancelou.\n"
        "- **Outliers**: valores extremos e a decisao de tratamento.\n"
        "- **Obesity: K-Means** (Parte Comum): EDA e as duas passadas do agrupamento.\n\n"
        "Use o menu lateral para trocar de pagina."
    )

with st.container(border=True):
    st.subheader(":material/table_chart: Dicionario das variaveis", anchor=False)
    dicionario = pd.DataFrame(
        [(coluna, *DICIONARIO_BANK[coluna]) for coluna in df.columns],
        columns=["Coluna", "Significado", "Tipo"],
    )
    st.dataframe(dicionario, hide_index=True, alt="Dicionario das variaveis do BankChurners")

with st.expander("Ver as primeiras linhas da base"):
    st.dataframe(df.head(20), hide_index=True, alt="Primeiras 20 linhas do BankChurners tratado")
