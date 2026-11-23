# [IA] Claude Code – ponto de entrada do dashboard: configuracao da pagina e navegacao
# Executar a partir da raiz do projeto:  streamlit run src/parte_especifica/dashboard.py
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Projeto AVD: BankChurners", page_icon=":material/credit_card:", layout="wide")

PASTA_PAGINAS = Path(__file__).parent / "app_pages"

# Cada integrante cria o seu arquivo em app_pages/. A pagina so entra no menu quando o arquivo existe,
# entao o dashboard continua funcionando enquanto as outras paginas nao ficam prontas.
PAGINAS = {
    "Parte Especifica": [
        ("inicio.py", "Inicio", ":material/home:",
         "Contexto do dataset, pergunta de pesquisa, publico-alvo e numeros gerais da base."),
        ("1_qualidade_dos_dados.py", "Qualidade dos dados", ":material/fact_check:",
         "Estrutura da base, valores Unknown e o tratamento escolhido."),
        ("2_distribuicoes.py", "Distribuicoes", ":material/bar_chart:",
         "Como cada variavel se distribui, com filtros por perfil de cliente."),
        ("3_relacoes.py", "Relacoes", ":material/scatter_plot:",
         "Relacoes entre as variaveis e com o cancelamento do cartao."),
        ("4_outliers.py", "Outliers", ":material/troubleshoot:",
         "Valores extremos: como foram identificados e tratados."),
    ],
    "Parte Comum": [
        ("5_parte_comum.py", "Obesity: K-Means", ":material/hub:",
         "EDA e as duas passadas do K-Means no dataset Obesity."),
    ],
}

navegacao = {
    secao: [
        st.Page(str(PASTA_PAGINAS / arquivo), title=titulo, icon=icone, help=ajuda, default=(arquivo == "inicio.py"))
        for arquivo, titulo, icone, ajuda in paginas
        if (PASTA_PAGINAS / arquivo).exists()
    ]
    for secao, paginas in PAGINAS.items()
}
navegacao = {secao: paginas for secao, paginas in navegacao.items() if paginas}

pagina = st.navigation(navegacao, position="sidebar")
st.title(pagina.title, anchor=False)
pagina.run()
