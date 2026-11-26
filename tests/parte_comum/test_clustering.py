# [IA] Claude Code – testes de clustering (TDD)
import numpy as np
import pandas as pd
import pytest

from parte_comum.clustering import (
    aplicar_mapa,
    ajustar_kmeans,
    k_cotovelo,
    kmeans_inercias,
    mapear_clusters,
    projetar_2d,
)


def _blobs() -> pd.DataFrame:
    """Três grupos bem separados em 2D (10 pontos cada)."""
    rng = np.random.default_rng(0)
    centros = [(0, 0), (10, 10), (-10, 10)]
    pontos = [rng.normal(c, 0.3, size=(10, 2)) for c in centros]
    return pd.DataFrame(np.vstack(pontos), columns=["x", "y"])


# ---------- kmeans_inercias ----------

def test_kmeans_inercias_devolve_um_valor_por_k():
    inercias = kmeans_inercias(_blobs(), range(2, 11))

    assert list(inercias.index) == list(range(2, 11))
    assert len(inercias) == 9


def test_kmeans_inercias_nao_cresce_com_k():
    inercias = kmeans_inercias(_blobs(), range(2, 11))

    assert inercias.is_monotonic_decreasing


def test_kmeans_inercias_e_reprodutivel_com_mesma_semente():
    a = kmeans_inercias(_blobs(), range(2, 6), random_state=42)
    b = kmeans_inercias(_blobs(), range(2, 6), random_state=42)

    pd.testing.assert_series_equal(a, b)


def test_kmeans_inercias_rejeita_k_maior_que_amostras():
    with pytest.raises(ValueError):
        kmeans_inercias(_blobs().head(5), [2, 6])


def test_kmeans_inercias_rejeita_k_menor_que_dois():
    with pytest.raises(ValueError):
        kmeans_inercias(_blobs(), [1, 2])


# ---------- ajustar_kmeans ----------

def test_ajustar_kmeans_separa_tres_grupos_obvios():
    labels = ajustar_kmeans(_blobs(), k=3)

    assert labels.shape == (30,)
    assert len(set(labels[:10])) == 1
    assert len(set(labels[10:20])) == 1
    assert len(set(labels[20:])) == 1
    assert len(set(labels)) == 3


def test_ajustar_kmeans_e_reprodutivel_com_mesma_semente():
    a = ajustar_kmeans(_blobs(), k=3, random_state=7)
    b = ajustar_kmeans(_blobs(), k=3, random_state=7)

    assert (a == b).all()


@pytest.mark.parametrize("k", [0, 1, 31])
def test_ajustar_kmeans_rejeita_k_invalido(k):
    with pytest.raises(ValueError):
        ajustar_kmeans(_blobs(), k=k)


# ---------- aplicar_mapa ----------

def test_aplicar_mapa_troca_cluster_pela_classe():
    previstas = aplicar_mapa(np.array([1, 0, 1]), {0: "a", 1: "b"})

    assert list(previstas) == ["b", "a", "b"]


def test_aplicar_mapa_rejeita_cluster_sem_mapeamento():
    with pytest.raises(ValueError, match="2"):
        aplicar_mapa(np.array([0, 2]), {0: "a", 1: "b"})


# ---------- mapear_clusters ----------

def test_mapear_clusters_escolhe_classe_majoritaria():
    labels = np.array([0, 0, 0, 1, 1, 1])
    y = pd.Series(["a", "a", "b", "b", "b", "a"])

    mapa = mapear_clusters(labels, y)

    assert mapa == {0: "a", 1: "b"}


def test_mapear_clusters_empate_e_deterministico():
    labels = np.array([0, 0, 0, 0])
    y = pd.Series(["b", "a", "b", "a"])

    mapa = mapear_clusters(labels, y)

    # empate: vence a classe que vem primeiro em ordem alfabética
    assert mapa == {0: "a"}


def test_mapear_clusters_rejeita_tamanhos_diferentes():
    with pytest.raises(ValueError):
        mapear_clusters(np.array([0, 1]), pd.Series(["a"]))


def test_mapear_clusters_aceita_y_com_indice_embaralhado():
    labels = np.array([0, 0, 1, 1])
    y = pd.Series(["a", "a", "b", "b"], index=[10, 3, 7, 1])

    assert mapear_clusters(labels, y) == {0: "a", 1: "b"}


# ---------- projetar_2d ----------

def test_projetar_2d_devolve_duas_colunas_e_mesmo_numero_de_linhas():
    X = pd.DataFrame(np.random.default_rng(1).normal(size=(20, 5)))

    proj = projetar_2d(X)

    assert list(proj.columns) == ["PC1", "PC2"]
    assert len(proj) == 20


def test_projetar_2d_rejeita_menos_de_duas_variaveis():
    with pytest.raises(ValueError):
        projetar_2d(pd.DataFrame({"x": [1.0, 2.0, 3.0]}))


# [IA] Claude Code – testes da escolha do k pelo cotovelo
def test_k_cotovelo_acha_o_joelho_de_curva_conhecida():
    # Queda forte ate k = 4 e quase plana depois: o cotovelo e k = 4
    inercias = pd.Series([100.0, 60.0, 30.0, 25.0, 22.0, 20.0, 19.0], index=range(2, 9))
    assert k_cotovelo(inercias) == 4


def test_k_cotovelo_usa_os_valores_do_indice():
    inercias = pd.Series([50.0, 20.0, 15.0, 14.0], index=[3, 5, 7, 9])
    assert k_cotovelo(inercias) == 5


def test_k_cotovelo_dados_de_blobs_aponta_tres_grupos():
    inercias = kmeans_inercias(_blobs(), range(2, 8))
    assert k_cotovelo(inercias) == 3


@pytest.mark.parametrize("inercias", [
    pd.Series([10.0, 5.0], index=[2, 3]),
    pd.Series([7.0, 3.0, 7.0], index=[2, 3, 4]),
])
def test_k_cotovelo_rejeita_series_invalidas(inercias):
    with pytest.raises(ValueError):
        k_cotovelo(inercias)
