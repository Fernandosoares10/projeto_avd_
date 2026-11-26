# [IA] Claude Code – pagina inicial: contexto, pergunta de pesquisa, publico-alvo e numeros gerais
import pandas as pd
import streamlit as st

from dados import CLIENTE_CANCELOU, COLUNA_ALVO, DICIONARIO_BANK, RAIZ_PROJETO, carregar_bank

# Textos definidos pelo grupo (a IA nao escreve pergunta de pesquisa nem publico-alvo)
PERGUNTA_DE_PESQUISA = 'Quais características do comportamento dos clientes estão mais associadas ao cancelamento do cartão de crédito e podem ajudar o banco a identificar clientes com maior risco de cancelamento?'
PUBLICO_ALVO = 'O dashboard é destinado às equipes de análise de dados, marketing e relacionamento com clientes do banco. A linguagem é objetiva e utiliza gráficos e indicadores para facilitar a identificação de padrões de comportamento, ajudando a compreender o cancelamento e a pensar em estratégias para retenção de clientes.'

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

# [IA] Claude Code – exportacao do relatorio completo (relatorio.pdf) direto pelo dashboard
CAMINHO_RELATORIO = RAIZ_PROJETO / "relatorio.pdf"


@st.cache_data
def bytes_relatorio() -> bytes:
    return CAMINHO_RELATORIO.read_bytes()


with st.container(border=True):
    st.subheader(":material/description: Relatorio do projeto", anchor=False)
    if CAMINHO_RELATORIO.exists():
        st.caption("Relatorio completo das duas partes (Obesity e BankChurners), com todas as visualizacoes e notas analiticas.")
        st.download_button(":material/picture_as_pdf: Baixar relatorio completo (PDF)", data=bytes_relatorio(),
                           file_name="relatorio_projeto_avd.pdf", mime="application/pdf", key="inicio_relatorio")
    else:
        st.info("O relatorio.pdf ainda nao foi gerado (python docs/montar_relatorio.py).")

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
