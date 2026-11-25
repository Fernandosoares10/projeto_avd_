# [IA] Claude Code – testes (TDD) das funções de outliers do BankChurners
import numpy as np
import pandas as pd
import pytest

from parte_especifica.outliers import (
    limites_iqr,
    mascara_outliers,
    resumo_outliers,
    taxa_alvo_por_grupo,
    tratar,
)

# 1..10 mais um valor extremo: Q1 = 3.5, Q3 = 8.5, IQR = 5.0 -> cercas -4 e 16
SERIE = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100], dtype=float)


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "valor": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100],
            "outra": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            "alvo": ["fica"] * 8 + ["sai", "sai", "sai"],
        }
    )


# ---------- limites_iqr ----------

def test_limites_iqr_calculados_a_mao():
    inferior, superior = limites_iqr(SERIE)

    assert inferior == pytest.approx(3.5 - 1.5 * 5.0)  # Q1=3.5, IQR=5.0
    assert superior == pytest.approx(8.5 + 1.5 * 5.0)  # Q3=8.5


def test_limites_iqr_multiplicador_maior_alarga_a_cerca():
    estreito = limites_iqr(SERIE, k=1.5)
    largo = limites_iqr(SERIE, k=3.0)

    assert largo[0] < estreito[0]
    assert largo[1] > estreito[1]


def test_limites_iqr_rejeita_k_negativo():
    with pytest.raises(ValueError):
        limites_iqr(SERIE, k=-1)


def test_limites_iqr_rejeita_k_nan():
    with pytest.raises(ValueError):
        limites_iqr(SERIE, k=float("nan"))


def test_limites_iqr_rejeita_serie_vazia():
    with pytest.raises(ValueError):
        limites_iqr(pd.Series([], dtype=float))


# ---------- mascara_outliers ----------

def test_mascara_iqr_marca_so_o_valor_extremo():
    mascara = mascara_outliers(SERIE, criterio="iqr")

    assert mascara.dtype == bool
    assert mascara.tolist() == [False] * 10 + [True]


def test_mascara_mantem_o_indice_original():
    serie = SERIE.copy()
    serie.index = list(range(100, 111))

    assert list(mascara_outliers(serie).index) == list(range(100, 111))


def test_mascara_z_marca_valor_acima_do_limite_de_z():
    serie = pd.Series([0.0] * 30 + [100.0])

    mascara = mascara_outliers(serie, criterio="z", z=3.0)

    assert mascara.sum() == 1
    assert bool(mascara.iloc[-1])


def test_mascara_serie_constante_nao_tem_outliers_nos_dois_criterios():
    constante = pd.Series([5.0] * 10)

    assert not mascara_outliers(constante, criterio="iqr").any()
    assert not mascara_outliers(constante, criterio="z").any()


def test_mascara_z_marca_tambem_valor_muito_abaixo_da_media():
    serie = pd.Series([0.0] * 30 + [-100.0])

    mascara = mascara_outliers(serie, criterio="z", z=3.0)

    assert mascara.sum() == 1
    assert bool(mascara.iloc[-1])


@pytest.mark.parametrize("criterio", ["iqr", "z"])
def test_mascara_ignora_ausentes_e_ainda_marca_o_extremo(criterio):
    serie = pd.Series([0.0] * 30 + [np.nan, 100.0])

    mascara = mascara_outliers(serie, criterio=criterio)

    assert not bool(mascara.iloc[30])  # o NaN nunca e outlier
    assert bool(mascara.iloc[31])      # o valor extremo continua sendo marcado
    assert mascara.dtype == bool


def test_mascara_iqr_zero_marca_todo_valor_diferente_da_maioria():
    # 95% iguais: Q1 = Q3 = 0, IQR = 0, as cercas colapsam em 0 e todo valor != 0 vira outlier.
    serie = pd.Series([0.0] * 95 + [1.0] * 5)

    assert mascara_outliers(serie, criterio="iqr").sum() == 5


def test_mascara_rejeita_criterio_desconhecido():
    with pytest.raises(ValueError, match="criterio"):
        mascara_outliers(SERIE, criterio="mediana")


# ---------- resumo_outliers ----------

def test_resumo_conta_abaixo_acima_e_percentual():
    df = pd.DataFrame({"x": [-100.0] + [10.0, 11.0, 12.0, 13.0, 14.0] * 2 + [100.0]})

    resumo = resumo_outliers(df, ["x"])

    linha = resumo.loc["x"]
    assert linha["abaixo"] == 1
    assert linha["acima"] == 1
    assert linha["total"] == 2
    assert linha["pct"] == pytest.approx(2 / 12 * 100)


def test_resumo_traz_limites_e_assimetria_por_coluna():
    resumo = resumo_outliers(_df(), ["valor", "outra"])

    assert list(resumo.index) == ["valor", "outra"]
    assert {"limite_inferior", "limite_superior", "assimetria", "total_z"} <= set(resumo.columns)
    assert resumo.loc["valor", "assimetria"] > 0
    assert resumo.loc["outra", "total"] == 0


def test_resumo_rejeita_coluna_inexistente():
    with pytest.raises(ValueError, match="nao_existe"):
        resumo_outliers(_df(), ["nao_existe"])


# ---------- tratar ----------

def test_tratar_manter_devolve_copia_igual():
    df = _df()

    resultado = tratar(df, ["valor"], "manter")

    pd.testing.assert_frame_equal(resultado, df)
    assert resultado is not df


def test_tratar_limitar_corta_nas_cercas_sem_perder_linhas():
    df = _df()
    _, superior = limites_iqr(df["valor"])

    resultado = tratar(df, ["valor"], "limitar")

    assert len(resultado) == len(df)
    assert resultado["valor"].max() == pytest.approx(superior)
    assert resultado.loc[0, "valor"] == 1  # quem estava dentro da cerca nao muda


def test_tratar_limitar_corta_tambem_a_cerca_inferior():
    df = pd.DataFrame({"x": [-100.0] + [10.0, 11.0, 12.0, 13.0, 14.0] * 2 + [100.0]})
    inferior, superior = limites_iqr(df["x"])

    resultado = tratar(df, ["x"], "limitar")

    assert resultado["x"].min() == pytest.approx(inferior)
    assert resultado["x"].max() == pytest.approx(superior)


def test_tratar_limitar_mantem_o_tipo_inteiro_da_coluna():
    df = _df()
    assert pd.api.types.is_integer_dtype(df["valor"])

    resultado = tratar(df, ["valor"], "limitar")

    assert pd.api.types.is_integer_dtype(resultado["valor"])
    assert resultado["valor"].max() == 16  # cerca 16,0 -> sem casas decimais numa contagem


def test_tratar_limitar_arredonda_a_cerca_para_dentro_em_coluna_inteira():
    # Q1 = 3,5, Q3 = 8,5, IQR = 5: com k = 1,25 a cerca superior e 14,75 (fracionaria).
    # Em coluna inteira o valor cortado e 14, o maior inteiro que ainda fica dentro da cerca.
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 100]})

    resultado = tratar(df, ["x"], "limitar", k=1.25)

    assert pd.api.types.is_integer_dtype(resultado["x"])
    assert resultado["x"].max() == 14
    assert resultado["x"].iloc[0] == 1


def test_tratar_remover_tira_as_linhas_com_outlier():
    resultado = tratar(_df(), ["valor"], "remover")

    assert len(resultado) == 10
    assert resultado["valor"].max() == 10


def test_tratar_remover_com_varias_colunas_remove_se_qualquer_for_outlier():
    df = pd.DataFrame(
        {
            "a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 100.0],
            "b": [100.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        }
    )

    resultado = tratar(df, ["a", "b"], "remover")

    assert len(resultado) == 8


def test_tratar_nunca_altera_o_dataframe_original():
    df = _df()
    copia = df.copy()

    for estrategia in ("manter", "limitar", "remover"):
        tratar(df, ["valor"], estrategia)

    pd.testing.assert_frame_equal(df, copia)


def test_tratar_so_mexe_nas_colunas_pedidas():
    resultado = tratar(_df(), ["valor"], "limitar")

    assert resultado["outra"].tolist() == _df()["outra"].tolist()
    assert resultado["alvo"].tolist() == _df()["alvo"].tolist()


def test_tratar_rejeita_estrategia_desconhecida():
    with pytest.raises(ValueError, match="estrategia"):
        tratar(_df(), ["valor"], "apagar_tudo")


def test_tratar_rejeita_coluna_nao_numerica():
    with pytest.raises(ValueError, match="alvo"):
        tratar(_df(), ["alvo"], "limitar")


# ---------- taxa_alvo_por_grupo ----------

def test_taxa_alvo_compara_outliers_com_o_resto():
    df = _df()  # o unico outlier de "valor" (a linha 10) e do grupo "sai"

    tabela = taxa_alvo_por_grupo(df, ["valor"], alvo="alvo", positivo="sai")

    linha = tabela.loc["valor"]
    assert linha["n_outliers"] == 1
    assert linha["taxa_outliers"] == pytest.approx(100.0)
    assert linha["taxa_demais"] == pytest.approx(2 / 10 * 100)


def test_taxa_alvo_sem_outliers_devolve_nan_na_taxa_dos_outliers():
    tabela = taxa_alvo_por_grupo(_df(), ["outra"], alvo="alvo", positivo="sai")

    assert tabela.loc["outra", "n_outliers"] == 0
    assert np.isnan(tabela.loc["outra", "taxa_outliers"])


def test_taxa_alvo_rejeita_alvo_inexistente():
    with pytest.raises(ValueError, match="alvo"):
        taxa_alvo_por_grupo(_df(), ["valor"], alvo="nao_existe", positivo="sai")
