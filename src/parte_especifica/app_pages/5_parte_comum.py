# [IA] Claude Code – pagina da Parte Comum: K-Means no Obesity com k ajustavel (cotovelo, grupos em PCA, mapeamento e metricas)
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dados import RAIZ_PROJETO, carregar_obesity

# `parte_comum` fica em src/, ao lado de `parte_especifica`; o Streamlit so poe a pasta do dashboard.py no sys.path.
CAMINHO_SRC = str(RAIZ_PROJETO / "src")
if CAMINHO_SRC not in sys.path:
    sys.path.insert(0, CAMINHO_SRC)

from parte_comum.avaliacao import avaliar  # noqa: E402
from parte_comum.clustering import (  # noqa: E402
    ajustar_kmeans,
    aplicar_mapa,
    k_cotovelo,
    kmeans_inercias,
    mapear_clusters,
    projetar_2d,
)
from parte_comum.preprocessing import ALVO, NUMERICAS, padronizar  # noqa: E402
from parte_comum.visualizacao import plotar_clusters, plotar_cotovelo  # noqa: E402

K_PADRAO = 7  # numero de classes reais; e o k fixo da Passada 2

df = carregar_obesity()


def inteiro_br(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


@st.cache_data
def variaveis_padronizadas() -> pd.DataFrame:
    return padronizar(df, NUMERICAS)


@st.cache_data
def inercias() -> pd.Series:
    return kmeans_inercias(variaveis_padronizadas(), range(2, 11))


@st.cache_data
def agrupar(k: int) -> dict:
    """K-Means com k grupos, projecao PCA, mapeamento cluster -> classe majoritaria e metricas."""
    X = variaveis_padronizadas()
    labels = ajustar_kmeans(X, k=k)
    mapa = mapear_clusters(labels, df[ALVO])
    return {
        "labels": labels,
        "proj": projetar_2d(X),
        "mapa": mapa,
        "resultado": avaliar(df[ALVO], aplicar_mapa(labels, mapa)),
    }


st.caption(
    f"Dataset Obesity (UCI 544). O K-Means agrupa as pessoas so pelas {len(NUMERICAS)} variaveis numericas, sem olhar a classe real; "
    "a classe so entra depois, para medir quanto os grupos coincidem com ela."
)

with st.container(horizontal=True):
    st.metric("Pessoas", inteiro_br(len(df)), border=True)
    st.metric("Variaveis no K-Means", f"{len(NUMERICAS)}", border=True)
    st.metric("Classes reais", f"{df[ALVO].nunique()}", border=True)

# ---------------------------------------------------------------- cotovelo
with st.container(border=True):
    st.subheader("Metodo do Cotovelo (k de 2 a 10)", anchor=False)
    # [IA] Claude Code – marcar o k do cotovelo (Passada 1) no grafico
    k_sugerido = k_cotovelo(inercias())
    st.pyplot(plotar_cotovelo(inercias(), k_escolhido=k_sugerido))
    st.caption(
        f"Em vermelho, o k da Passada 1 (k = {k_sugerido}), dado pelo criterio da maior distancia ate a reta. "
        f"O controle abaixo comeca em k = {K_PADRAO} (numero de classes reais, Passada 2); mude para comparar."
    )

# ---------------------------------------------------------------- grupos e metricas
with st.container(border=True):
    st.subheader("Grupos, mapeamento e metricas", anchor=False)
    k = st.slider("Numero de grupos (k)", min_value=2, max_value=10, value=K_PADRAO, key="pc_k")
    dados_k = agrupar(k)
    resultado = dados_k["resultado"]

    with st.container(horizontal=True):
        st.metric("Grupos (k)", f"{k}", border=True)
        st.metric("Acuracia", f"{resultado['acuracia'] * 100:.1f}%", border=True,
                  help="Percentual de pessoas cuja classe real e a classe majoritaria do grupo em que caiu.")
        st.metric("Precisao (macro)", f"{resultado['precisao'] * 100:.1f}%", border=True)
        st.metric("Recall (macro)", f"{resultado['recall'] * 100:.1f}%", border=True)

    st.pyplot(plotar_clusters(dados_k["proj"], dados_k["labels"]))
    st.caption(f"Projecao em 2 componentes principais (PCA) so para desenhar; o agrupamento usa as {len(NUMERICAS)} variaveis.")

    tamanhos = pd.Series(dados_k["labels"]).value_counts().sort_index()
    mapeamento = pd.DataFrame(
        {"Classe majoritaria": pd.Series(dados_k["mapa"]), "Pessoas no grupo": tamanhos}
    ).rename_axis("Grupo")
    st.dataframe(mapeamento, alt="Classe majoritaria e tamanho de cada grupo")

    sem_grupo = sorted(set(df[ALVO].unique()) - set(dados_k["mapa"].values()))
    if sem_grupo:
        st.warning(
            f"Sem grupo proprio: {', '.join(sem_grupo)}. Nenhum grupo tem essa classe como maioria, entao ela nunca "
            "e prevista e seu recall e 0%."
        )

    st.markdown("**Matriz de confusao** (linhas: classe real; colunas: classe prevista pelo grupo)")
    st.dataframe(resultado["matriz_confusao"], alt="Matriz de confusao do K-Means contra a classe real")
    if k == K_PADRAO:
        st.caption("Com k = 7 o resultado e o mesmo da Passada 2 (notebook kmeans_passada2.ipynb): mesmo metodo, mesma semente.")


# ---------------------------------------------------------------- transicao animada entre as passadas
# [IA] Claude Code – animacao da transicao Passada 1 (k do cotovelo) -> Passada 2 (k = 7) na mesma projecao PCA
ORDEM_CLASSES = [
    "Insufficient_Weight", "Normal_Weight", "Overweight_Level_I", "Overweight_Level_II",
    "Obesity_Type_I", "Obesity_Type_II", "Obesity_Type_III",
]
CORES_CLASSES = dict(zip(ORDEM_CLASSES, ["#4C72B0", "#55A868", "#CCB974", "#DD8452", "#C44E52", "#8172B3", "#2F2F2F"]))


@st.cache_data
def figura_transicao(k_passada1: int, k_passada2: int) -> go.Figure:
    """Um unico conjunto de pontos (mesma ordem e posicao); entre os quadros so muda a cor = classe mapeada do grupo."""
    proj = projetar_2d(variaveis_padronizadas())
    quadros = []
    for nome, k_passada in [(f"Passada 1 (k = {k_passada1})", k_passada1), (f"Passada 2 (k = {k_passada2})", k_passada2)]:
        grupo = agrupar(k_passada)
        classe_mapeada = aplicar_mapa(grupo["labels"], grupo["mapa"])
        quadros.append((nome, classe_mapeada))

    def pontos(classe_mapeada) -> go.Scattergl:
        return go.Scattergl(
            x=proj["PC1"], y=proj["PC2"], mode="markers", showlegend=False,
            marker={"color": [CORES_CLASSES[c] for c in classe_mapeada], "size": 5, "opacity": 0.6},
            customdata=list(zip(classe_mapeada, df[ALVO])),
            hovertemplate="Grupo mapeado: %{customdata[0]}<br>Classe real: %{customdata[1]}<extra></extra>",
        )

    # tracos vazios so para a legenda de cores (uma entrada por classe)
    legenda = [
        go.Scattergl(x=[None], y=[None], mode="markers", name=c, marker={"color": CORES_CLASSES[c], "size": 9})
        for c in ORDEM_CLASSES
    ]
    fig = go.Figure(
        data=[pontos(quadros[0][1]), *legenda],
        frames=[go.Frame(data=[pontos(classe)], traces=[0], name=nome) for nome, classe in quadros],
    )
    passos = [
        {"label": nome, "method": "animate",
         "args": [[nome], {"mode": "immediate", "frame": {"duration": 900, "redraw": True}, "transition": {"duration": 600}}]}
        for nome, _ in quadros
    ]
    fig.update_layout(
        title="Transicao entre as passadas: grupo mapeado de cada pessoa (mesma projecao PCA)",
        xaxis_title="Componente principal 1", yaxis_title="Componente principal 2",
        legend_title_text="Classe majoritaria do grupo", height=560,
        updatemenus=[{
            "type": "buttons", "showactive": False, "x": 0, "y": -0.12, "xanchor": "left", "yanchor": "top",
            "buttons": [{"label": "▶ Animar", "method": "animate",
                         "args": [None, {"frame": {"duration": 1500, "redraw": True}, "transition": {"duration": 600},
                                         "fromcurrent": False, "mode": "immediate"}]}],
        }],
        sliders=[{"active": 0, "x": 0.12, "y": -0.08, "len": 0.88, "currentvalue": {"prefix": "Quadro: "}, "steps": passos}],
    )
    return fig


with st.container(border=True):
    st.subheader("Transicao animada: Passada 1 -> Passada 2", anchor=False)
    k_p1 = k_cotovelo(inercias())
    p1, p2 = agrupar(k_p1), agrupar(K_PADRAO)
    col_p1, col_p2 = st.columns(2)
    for coluna, nome, k_passada, dados_passada in [(col_p1, "Passada 1", k_p1, p1), (col_p2, "Passada 2", K_PADRAO, p2)]:
        with coluna:
            sem = sorted(set(ORDEM_CLASSES) - set(dados_passada["mapa"].values()))
            st.metric(f"{nome}: acuracia (k = {k_passada})", f"{dados_passada['resultado']['acuracia'] * 100:.1f}%", border=True)
            st.caption(f"Classes sem grupo: {', '.join(sem) if sem else 'nenhuma'}")
    st.plotly_chart(figura_transicao(k_p1, K_PADRAO), key="pc_transicao")
    st.caption(
        "Os pontos ficam no mesmo lugar: so muda a cor, que e a classe majoritaria do grupo em que a pessoa caiu. "
        "Use o botao Animar ou o controle abaixo do grafico. Passe o mouse para ver a classe real de cada pessoa."
    )
