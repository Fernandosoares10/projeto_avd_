# [IA] Claude Code – testes (TDD) das taxas de cancelamento por categoria e por recorte
import numpy as np
import pandas as pd
import pytest

from parte_especifica.taxas import taxa_do_recorte, taxa_por_categoria


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "grupo": [2, 2, 1, 1, 1, 3],
            "alvo": ["sai", "sai", "sai", "fica", "fica", "fica"],
        }
    )


# ---------- taxa_por_categoria ----------

def test_taxa_por_categoria_calcula_n_positivos_e_taxa_a_mao():
    tabela = taxa_por_categoria(_df(), "grupo", alvo="alvo", positivo="sai")

    assert tabela.loc[1, "n"] == 3
    assert tabela.loc[1, "positivos"] == 1
    assert tabela.loc[1, "taxa"] == pytest.approx(100 / 3)
    assert tabela.loc[2, "taxa"] == pytest.approx(100.0)
    assert tabela.loc[3, "taxa"] == pytest.approx(0.0)


def test_taxa_por_categoria_ignora_categoria_ausente():
    df = pd.concat([_df(), pd.DataFrame({"grupo": [np.nan], "alvo": ["sai"]})], ignore_index=True)

    tabela = taxa_por_categoria(df, "grupo", alvo="alvo", positivo="sai")

    assert tabela["n"].sum() == 6  # a linha com grupo NaN nao entra
    assert tabela["positivos"].sum() == 3  # nem o "sai" dela


def test_taxa_por_categoria_com_positivo_inexistente_da_taxa_zero_em_todas():
    tabela = taxa_por_categoria(_df(), "grupo", alvo="alvo", positivo="nunca_aparece")

    assert (tabela["taxa"] == 0).all()
    assert (tabela["positivos"] == 0).all()


def test_taxa_por_categoria_com_dataframe_vazio_devolve_tabela_vazia():
    vazio = pd.DataFrame({"grupo": pd.Series([], dtype=int), "alvo": pd.Series([], dtype=object)})

    assert taxa_por_categoria(vazio, "grupo", alvo="alvo", positivo="sai").empty


def test_taxa_por_categoria_nao_altera_o_dataframe_original():
    df = _df()
    copia = df.copy()

    taxa_por_categoria(df, "grupo", alvo="alvo", positivo="sai")

    pd.testing.assert_frame_equal(df, copia)


def test_taxa_por_categoria_rejeita_coluna_inexistente():
    with pytest.raises(ValueError, match="nao_existe"):
        taxa_por_categoria(_df(), "nao_existe", alvo="alvo", positivo="sai")


def test_taxa_por_categoria_rejeita_alvo_inexistente():
    with pytest.raises(ValueError, match="alvo_errado"):
        taxa_por_categoria(_df(), "grupo", alvo="alvo_errado", positivo="sai")


# ---------- taxa_do_recorte ----------

def test_taxa_do_recorte_e_o_percentual_de_positivos_dentro_do_recorte():
    df = _df()

    # grupos 1 e 2 -> 5 linhas, 3 positivos
    assert taxa_do_recorte(df, df["grupo"] <= 2, alvo="alvo", positivo="sai") == pytest.approx(60.0)


def test_taxa_do_recorte_e_posicional_e_ignora_o_indice_do_dataframe():
    df = _df()
    df.index = [10, 11, 12, 13, 14, 15]
    recorte = pd.Series([True, True, True, True, True, False])  # indice 0..5, diferente do de df

    assert taxa_do_recorte(df, recorte, alvo="alvo", positivo="sai") == pytest.approx(60.0)


def test_taxa_do_recorte_com_dataframe_vazio_devolve_nan():
    vazio = pd.DataFrame({"alvo": pd.Series([], dtype=object)})

    assert np.isnan(taxa_do_recorte(vazio, pd.Series([], dtype=bool), alvo="alvo", positivo="sai"))


def test_taxa_do_recorte_vazio_devolve_nan():
    df = _df()

    assert np.isnan(taxa_do_recorte(df, df["grupo"] > 99, alvo="alvo", positivo="sai"))


def test_taxa_do_recorte_rejeita_mascara_de_tamanho_diferente():
    with pytest.raises(ValueError):
        taxa_do_recorte(_df(), pd.Series([True, False]), alvo="alvo", positivo="sai")
