# [IA] Claude Code – gráficos do cotovelo e dos clusters (Passada 1)
"""Gráficos da Passada 1: Método do Cotovelo e visualização dos clusters.

Usa `Figure` direto (sem pyplot) para não acumular figuras no estado global,
o que importa quando o Streamlit reexecuta o script a cada interação.
"""

import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def plotar_cotovelo(inercias: pd.Series, k_escolhido: int | None = None) -> Figure:
    """Curva inércia x k. O índice da série são os valores de k.

    Com `k_escolhido`, marca o ponto do cotovelo e adiciona legenda.
    """
    if inercias.empty:
        raise ValueError("A série de inércias está vazia")

    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()
    ax.plot(inercias.index, inercias.values, marker="o", label="Inércia")
    # [IA] Claude Code – destacar o k escolhido pelo cotovelo e adicionar legenda
    if k_escolhido is not None:
        if k_escolhido not in inercias.index:
            raise ValueError(f"k_escolhido={k_escolhido} não está entre os k da série")
        ax.plot([k_escolhido], [inercias.loc[k_escolhido]], marker="o", markersize=12,
                color="#C44E52", linestyle="", label=f"Cotovelo: k = {k_escolhido}")
        ax.legend()
    ax.set_xticks(list(inercias.index))
    ax.set_xlabel("k (número de clusters)")
    ax.set_ylabel("Inércia")
    ax.set_title("Método do Cotovelo")
    ax.grid(alpha=0.3)
    return fig


def plotar_clusters(proj: pd.DataFrame, labels: np.ndarray) -> Figure:
    """Dispersão PC1 x PC2 com uma cor (e uma entrada de legenda) por cluster."""
    labels = np.asarray(labels)
    if len(proj) != len(labels):
        raise ValueError(
            f"proj ({len(proj)}) e labels ({len(labels)}) têm tamanhos diferentes"
        )

    fig = Figure(figsize=(7, 5))
    ax = fig.subplots()
    for cluster in sorted(set(labels)):
        mascara = labels == cluster
        ax.scatter(
            proj["PC1"].to_numpy()[mascara],
            proj["PC2"].to_numpy()[mascara],
            s=18,
            alpha=0.7,
            label=f"Cluster {cluster}",
        )
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Clusters do K-Means projetados em 2D (PCA)")
    ax.legend()
    ax.grid(alpha=0.3)
    return fig
