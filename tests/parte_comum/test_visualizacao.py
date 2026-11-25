# [IA] Claude Code – testes dos gráficos (TDD)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

from parte_comum.visualizacao import plotar_clusters, plotar_cotovelo


@pytest.fixture(autouse=True)
def _fechar_figuras():
    yield
    plt.close("all")


def test_plotar_cotovelo_devolve_figura_com_rotulos():
    inercias = pd.Series([100.0, 60.0, 40.0], index=[2, 3, 4])

    fig = plotar_cotovelo(inercias)

    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == "k (número de clusters)"
    assert ax.get_ylabel() == "Inércia"
    assert ax.get_title() != ""
    assert list(ax.lines[0].get_xdata()) == [2, 3, 4]
    assert list(ax.lines[0].get_ydata()) == [100.0, 60.0, 40.0]


def test_graficos_nao_ficam_registrados_no_pyplot():
    # Evita vazamento de figuras quando o Streamlit reexecuta o script.
    plotar_cotovelo(pd.Series([2.0, 1.0], index=[2, 3]))
    plotar_clusters(
        pd.DataFrame({"PC1": [0.0, 1.0], "PC2": [0.0, 1.0]}), np.array([0, 1])
    )

    assert plt.get_fignums() == []


def test_plotar_cotovelo_rejeita_serie_vazia():
    with pytest.raises(ValueError):
        plotar_cotovelo(pd.Series(dtype=float))


def test_plotar_clusters_desenha_um_grupo_por_cluster():
    proj = pd.DataFrame({"PC1": [0.0, 1.0, 2.0, 3.0], "PC2": [0.0, 1.0, 0.0, 1.0]})
    labels = np.array([0, 0, 1, 1])

    fig = plotar_clusters(proj, labels)

    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == "PC1"
    assert ax.get_ylabel() == "PC2"
    assert len(ax.get_legend().get_texts()) == 2
    assert len(ax.collections) == 2
    assert [len(c.get_offsets()) for c in ax.collections] == [2, 2]


def test_plotar_clusters_rejeita_tamanhos_diferentes():
    proj = pd.DataFrame({"PC1": [0.0, 1.0], "PC2": [0.0, 1.0]})

    with pytest.raises(ValueError):
        plotar_clusters(proj, np.array([0]))
