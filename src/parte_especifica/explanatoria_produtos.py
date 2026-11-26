# [IA] Claude Code – visualizacao explanatoria 2 (cancelamento por numero de produtos), exibida na pagina Relacoes
"""Grafico, metricas e nota analitica da explanatoria 2. Usa sempre a base inteira, sem os filtros da pagina."""
import plotly.express as px
import streamlit as st

from dados import CLIENTE_CANCELOU, COLUNA_ALVO, CORES_SITUACAO, carregar_bank
from taxas import taxa_do_recorte, taxa_por_categoria

# Nota analitica e titulo escritos pelo grupo, iguais ao notebook viz_explanatoria_2
TITULO_EXPL2 = 'Clientes com Menos Produtos Contratados Apresentam Maior Taxa de Cancelamento'
NOTA_EXPL2_O_QUE_MOSTRA = 'O gráfico mostra a taxa de cancelamento dos clientes de acordo com a quantidade de produtos que possuem no banco, de 1 a 6. Também apresenta a quantidade de clientes em cada grupo e uma linha de referência com a taxa geral de cancelamento da base, que é de 16,1%.'
NOTA_EXPL2_INSIGHT = 'Clientes que possuem apenas 1 ou 2 produtos apresentam uma taxa de cancelamento maior, de 26,9%. Já entre os clientes que possuem de 4 a 6 produtos, a taxa cai para 11,4%. Ou seja, clientes com menos produtos cancelam aproximadamente 2,4 vezes mais. Outro ponto importante é que os clientes com 1 ou 2 produtos representam apenas 21,3% da base, mas correspondem a 35,6% de todos os cancelamentos. Isso mostra que ter poucos produtos contratados pode ser um sinal de maior risco de cancelamento.'
NOTA_EXPL2_POR_QUE = 'Escolhemos o gráfico de barras porque ele facilita a comparação da taxa de cancelamento entre diferentes quantidades de produtos. O vermelho destaca os grupos com maior taxa de cancelamento, enquanto a linha da média permite comparar cada grupo com a taxa geral da base.'

COLUNA_PRODUTOS = "Total_Relationship_Count"


def _inteiro_br(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def _dec_br(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


@st.cache_data
def analisar_produtos() -> dict:
    """Numeros e grafico da explanatoria 2 sobre a base inteira."""
    df = carregar_bank()
    cancelou = df[COLUNA_ALVO] == CLIENTE_CANCELOU
    por_produtos = taxa_por_categoria(df, COLUNA_PRODUTOS, COLUNA_ALVO, CLIENTE_CANCELOU)
    poucos = df[COLUNA_PRODUTOS] <= 2
    muitos = df[COLUNA_PRODUTOS] >= 4
    taxa_base = cancelou.mean() * 100
    taxa_poucos = taxa_do_recorte(df, poucos, COLUNA_ALVO, CLIENTE_CANCELOU)
    taxa_muitos = taxa_do_recorte(df, muitos, COLUNA_ALVO, CLIENTE_CANCELOU)

    grafico = por_produtos.reset_index().assign(
        Rotulo=lambda d: d[COLUNA_PRODUTOS].astype(int).astype(str) + " (n = " + d["n"].map(_inteiro_br) + ")",
        Grupo=lambda d: d[COLUNA_PRODUTOS].map(lambda p: "1 ou 2 produtos" if p <= 2 else "3 ou mais produtos"),
    )
    fig = px.bar(
        grafico, x="Rotulo", y="taxa", color="Grupo", text=grafico["taxa"].map(lambda t: f"{t:.1f}%"),
        color_discrete_map={"1 ou 2 produtos": CORES_SITUACAO["Cancelou"], "3 ou mais produtos": "#8C8C8C"},
        title=TITULO_EXPL2,
        labels={"Rotulo": "Numero de produtos do banco que o cliente tem", "taxa": "Taxa de cancelamento (%)", "Grupo": ""},
    )
    fig.add_hline(y=taxa_base, line_dash="dash", line_color="black",
                  annotation_text=f"Base toda: {_dec_br(taxa_base)}%", annotation_position="top right")
    fig.update_traces(textposition="outside", cliponaxis=False)

    return {
        "fig": fig,
        "taxa_poucos": taxa_poucos,
        "taxa_muitos": taxa_muitos,
        "razao": taxa_poucos / taxa_muitos,
    }


def secao_produtos() -> None:
    """Desenha a explanatoria 2: metricas, grafico e nota analitica."""
    d = analisar_produtos()
    st.subheader("Visualizacao explanatoria 2: produtos do banco e cancelamento", anchor=False)
    st.caption("Calculada sobre a base inteira (os filtros laterais desta pagina nao se aplicam a este grafico).")
    with st.container(horizontal=True):
        st.metric("Cancelam com 1 ou 2 produtos", f"{d['taxa_poucos']:.1f}%", border=True)
        st.metric("Cancelam com 4 a 6 produtos", f"{d['taxa_muitos']:.1f}%", border=True)
        st.metric("Diferenca entre os dois grupos", f"{d['razao']:.1f}x", border=True)
    st.plotly_chart(d["fig"], key="rel_expl2")
    with st.expander("Nota analitica", icon=":material/edit_note:"):
        st.markdown(f"**O que esta sendo mostrado:** {NOTA_EXPL2_O_QUE_MOSTRA}")
        st.markdown(f"**Qual insight pode ser extraido:** {NOTA_EXPL2_INSIGHT}")
        st.markdown(f"**Por que este tipo de visualizacao:** {NOTA_EXPL2_POR_QUE}")
