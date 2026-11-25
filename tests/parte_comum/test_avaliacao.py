# [IA] Claude Code – testes de avaliação (TDD)
import numpy as np
import pandas as pd
import pytest

from parte_comum.avaliacao import avaliar


def test_avaliar_predicao_perfeita_da_um_em_tudo():
    y = pd.Series(["a", "b", "a", "b"])

    r = avaliar(y, y)

    assert r["acuracia"] == 1.0
    assert r["precisao"] == 1.0
    assert r["recall"] == 1.0


def test_avaliar_caso_calculado_a_mao():
    y_true = ["a", "a", "b", "b"]
    y_pred = ["a", "b", "b", "b"]

    r = avaliar(y_true, y_pred)

    # acurácia 3/4; precisão a=1, b=2/3; recall a=1/2, b=1 (médias macro)
    assert r["acuracia"] == pytest.approx(0.75)
    assert r["precisao"] == pytest.approx((1 + 2 / 3) / 2)
    assert r["recall"] == pytest.approx(0.75)


def test_avaliar_matriz_de_confusao_tem_rotulos_de_linhas_e_colunas():
    r = avaliar(["a", "a", "b", "b"], ["a", "b", "b", "b"])

    matriz = r["matriz_confusao"]

    assert isinstance(matriz, pd.DataFrame)
    assert list(matriz.index) == ["a", "b"]
    assert list(matriz.columns) == ["a", "b"]
    assert matriz.loc["a", "b"] == 1
    assert matriz.loc["b", "b"] == 2


def test_avaliar_classe_nunca_predita_nao_quebra_e_conta_zero(recwarn):
    # "b" nunca é predita: precisão de b indefinida, tratada como 0
    r = avaliar(["a", "b"], ["a", "a"])

    assert r["precisao"] == pytest.approx(0.25)
    assert len(recwarn) == 0


def test_avaliar_inclui_classe_so_presente_nas_predicoes():
    r = avaliar(["a", "a"], ["a", "c"])

    assert "c" in r["matriz_confusao"].columns
    assert "c" in r["matriz_confusao"].index


def test_avaliar_rejeita_tamanhos_diferentes():
    with pytest.raises(ValueError):
        avaliar(["a", "b"], ["a"])


def test_avaliar_rejeita_entrada_vazia():
    with pytest.raises(ValueError):
        avaliar([], [])


def test_avaliar_aceita_arrays_numpy():
    r = avaliar(np.array(["a", "b"]), np.array(["a", "b"]))

    assert r["acuracia"] == 1.0
