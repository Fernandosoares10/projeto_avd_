# [IA] Claude Code – pagina da Parte Comum: K-Means no Obesity com k ajustavel (cotovelo, grupos em PCA, mapeamento e metricas)
import sys

import pandas as pd
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
    st.pyplot(plotar_cotovelo(inercias()))
    st.caption(
        "A inercia cai de forma gradual, sem um joelho nitido: o metodo sozinho nao aponta um k unico. "
        f"Usamos k = {K_PADRAO} (numero de classes reais) como ponto de partida; mude abaixo para comparar."
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
