# [IA] Claude Code – testes dos testes estatisticos sem scipy (valores de tabela conhecidos)
import numpy as np
import pandas as pd
import pytest

from parte_comum.estatistica import (
    kruskal_wallis,
    mann_whitney,
    p_valor_normal_bilateral,
    p_valor_qui_quadrado,
    qui_quadrado_contingencia,
)


@pytest.mark.parametrize("estatistica, graus, esperado", [
    (3.841459, 1, 0.05),   # valores criticos classicos da tabela qui-quadrado
    (5.991465, 2, 0.05),
    (6.634897, 1, 0.01),
    (18.307038, 10, 0.05),
])
def test_p_valor_qui_quadrado_bate_com_a_tabela(estatistica, graus, esperado):
    assert p_valor_qui_quadrado(estatistica, graus) == pytest.approx(esperado, rel=1e-5)


def test_p_valor_normal_bilateral_de_1_96_e_5_por_cento():
    assert p_valor_normal_bilateral(1.959964) == pytest.approx(0.05, rel=1e-5)


def test_qui_quadrado_de_tabela_independente_e_zero():
    tabela = pd.DataFrame([[10, 20, 30], [20, 40, 60]])
    qui2, p, graus = qui_quadrado_contingencia(tabela)
    assert qui2 == pytest.approx(0)
    assert p == pytest.approx(1)
    assert graus == 2


def test_qui_quadrado_2x2_usa_correcao_de_yates():
    # O=[[10,20],[20,10]], E=15 em todas as celulas; com Yates |O-E| vira 4,5: 4 * 4,5² / 15 = 5,4
    qui2, _, graus = qui_quadrado_contingencia(pd.DataFrame([[10, 20], [20, 10]]))
    assert graus == 1
    assert qui2 == pytest.approx(5.4)


def test_qui_quadrado_rejeita_tabela_com_uma_linha():
    with pytest.raises(ValueError):
        qui_quadrado_contingencia(pd.DataFrame([[1, 2, 3]]))


def test_kruskal_de_grupos_iguais_e_zero():
    h, p = kruskal_wallis([1, 2, 3], [1, 2, 3], [1, 2, 3])
    assert h == pytest.approx(0)
    assert p == pytest.approx(1)


def test_kruskal_sem_empates_bate_com_a_formula():
    # postos: grupo A = 1,2,3 (soma 6), grupo B = 4,5,6 (soma 15); H = 12/42 * (36/3 + 225/3) - 21 = 3,857...
    h, _ = kruskal_wallis([1, 2, 3], [4, 5, 6])
    assert h == pytest.approx(12 / 42 * (36 / 3 + 225 / 3) - 21)


def test_mann_whitney_com_grupos_totalmente_separados():
    u, p = mann_whitney([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
    assert u == 0
    assert p < 0.05


def test_mann_whitney_com_grupos_iguais_nao_rejeita():
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    _, p = mann_whitney(x, x.copy())
    assert p > 0.9


@pytest.mark.parametrize("grupos", [([1, 2], []), ([], [1, 2])])
def test_mann_whitney_rejeita_grupo_vazio(grupos):
    with pytest.raises(ValueError):
        mann_whitney(*grupos)
