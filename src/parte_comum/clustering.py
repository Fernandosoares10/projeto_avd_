# [IA] Claude Code – K-Means, mapeamento cluster-classe e projeção PCA (Passada 1)
"""K-Means, mapeamento cluster -> classe e projeção 2D para visualização."""

from collections.abc import Iterable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

SEMENTE = 42
N_INIT = 10


def _validar_k(ks: list[int], n_amostras: int) -> None:
    """Levanta ValueError se algum k estiver fora de [2, n_amostras]."""
    invalidos = [k for k in ks if k < 2 or k > n_amostras]
    if invalidos:
        raise ValueError(
            f"k deve estar entre 2 e {n_amostras} (nº de amostras); inválidos: {invalidos}"
        )


def kmeans_inercias(
    X: pd.DataFrame, ks: Iterable[int], random_state: int = SEMENTE
) -> pd.Series:
    """Inércia do K-Means para cada k em `ks` (base do Método do Cotovelo)."""
    ks = list(ks)
    _validar_k(ks, len(X))

    inercias = [
        KMeans(n_clusters=k, n_init=N_INIT, random_state=random_state).fit(X).inertia_
        for k in ks
    ]
    return pd.Series(inercias, index=ks, name="inercia", dtype=float)


def ajustar_kmeans(
    X: pd.DataFrame, k: int, random_state: int = SEMENTE
) -> np.ndarray:
    """Ajusta o K-Means com `k` clusters e devolve o rótulo de cada linha."""
    _validar_k([k], len(X))
    modelo = KMeans(n_clusters=k, n_init=N_INIT, random_state=random_state)
    return modelo.fit_predict(X)


def mapear_clusters(labels: np.ndarray, y: pd.Series) -> dict[int, object]:
    """Associa cada cluster à classe majoritária dentro dele.

    Em caso de empate vence a classe que vem primeiro em ordem alfabética,
    para o resultado ser determinístico.
    """
    if len(labels) != len(y):
        raise ValueError(
            f"labels ({len(labels)}) e y ({len(y)}) têm tamanhos diferentes"
        )

    # np.asarray descarta o índice de y: a associação é posicional.
    dados = pd.DataFrame({"cluster": np.asarray(labels), "classe": np.asarray(y)})
    mapa: dict[int, object] = {}
    for cluster, grupo in dados.groupby("cluster"):
        contagem = grupo["classe"].value_counts()
        empatadas = sorted(contagem[contagem == contagem.max()].index)
        mapa[int(cluster)] = empatadas[0]
    return mapa


def aplicar_mapa(labels: np.ndarray, mapa: dict[int, object]) -> np.ndarray:
    """Troca o rótulo de cada cluster pela classe prevista em `mapa`.

    Levanta ValueError se algum cluster não estiver no mapa.
    """
    labels = np.asarray(labels)
    sem_mapa = sorted({int(c) for c in labels} - set(mapa))
    if sem_mapa:
        raise ValueError(f"Clusters sem classe mapeada: {sem_mapa}")
    return np.array([mapa[int(c)] for c in labels])


def projetar_2d(X: pd.DataFrame, random_state: int = SEMENTE) -> pd.DataFrame:
    """Projeta `X` em 2 componentes principais (colunas PC1 e PC2)."""
    X = pd.DataFrame(X)
    if X.shape[1] < 2:
        raise ValueError("A projeção 2D exige pelo menos 2 variáveis")

    componentes = PCA(n_components=2, random_state=random_state).fit_transform(X)
    return pd.DataFrame(componentes, columns=["PC1", "PC2"], index=X.index)
