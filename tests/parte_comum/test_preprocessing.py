# [IA] Claude Code – testes de preprocessing (TDD)
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from parte_comum.preprocessing import (
    ALVO,
    NUMERICAS,
    carregar_obesity,
    padronizar,
)

CAMINHO_OBESITY = (
    Path(__file__).resolve().parents[2] / "data" / "parte_comum" / "obesity.csv"
)


def _df_exemplo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 4.0],
            "b": [10.0, 20.0, 30.0, 40.0],
            "texto": ["x", "y", "x", "y"],
        }
    )


def test_padronizar_gera_media_zero_e_desvio_um():
    df = _df_exemplo()

    resultado = padronizar(df, ["a", "b"])

    assert resultado.mean().abs().max() < 1e-9
    assert np.allclose(resultado.std(ddof=0), 1.0)


def test_padronizar_nao_altera_dataframe_original():
    df = _df_exemplo()
    copia = df.copy()

    padronizar(df, ["a", "b"])

    pd.testing.assert_frame_equal(df, copia)


def test_padronizar_devolve_apenas_colunas_pedidas_e_mantem_indice():
    df = _df_exemplo()
    df.index = [5, 6, 7, 8]

    resultado = padronizar(df, ["a"])

    assert list(resultado.columns) == ["a"]
    assert list(resultado.index) == [5, 6, 7, 8]


def test_padronizar_rejeita_coluna_nao_numerica():
    with pytest.raises(ValueError, match="texto"):
        padronizar(_df_exemplo(), ["a", "texto"])


def test_padronizar_rejeita_coluna_inexistente():
    with pytest.raises(ValueError, match="nao_existe"):
        padronizar(_df_exemplo(), ["nao_existe"])


def test_padronizar_rejeita_valores_ausentes():
    df = pd.DataFrame({"a": [1.0, np.nan, 3.0]})

    with pytest.raises(ValueError, match="a"):
        padronizar(df, ["a"])


def test_padronizar_coluna_constante_vira_zero_sem_nan():
    df = pd.DataFrame({"c": [5.0, 5.0, 5.0]})

    resultado = padronizar(df, ["c"])

    assert (resultado["c"] == 0).all()


def test_carregar_obesity_tem_alvo_e_variaveis_numericas():
    df = carregar_obesity(CAMINHO_OBESITY)

    assert ALVO in df.columns
    assert set(NUMERICAS).issubset(df.columns)
    assert len(df) == 2111
    assert df[ALVO].nunique() == 7


def test_carregar_obesity_arquivo_inexistente_levanta_erro_claro():
    with pytest.raises(FileNotFoundError):
        carregar_obesity(Path("nao/existe.csv"))
