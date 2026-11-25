# [IA] Claude Code – deteccao e tratamento de outliers do BankChurners (IQR e z-score)
"""Funcoes de outliers sem dependencia do Streamlit.

Usadas pelo notebook `eda_outliers.ipynb` e pela pagina `app_pages/4_outliers.py`,
para que as duas mostrem exatamente os mesmos numeros.
"""
import math
from collections.abc import Sequence

import numpy as np
import pandas as pd

K_IQR = 1.5
Z_LIMITE = 3.0
CRITERIOS = ("iqr", "z")
ESTRATEGIAS = ("manter", "limitar", "remover")


def _validar_colunas(df: pd.DataFrame, colunas: Sequence[str]) -> list[str]:
    """Garante que as colunas existem e sao numericas. Devolve a lista de colunas."""
    colunas = list(colunas)
    ausentes = [c for c in colunas if c not in df.columns]
    if ausentes:
        raise ValueError(f"Colunas inexistentes: {ausentes}")
    nao_numericas = [c for c in colunas if not pd.api.types.is_numeric_dtype(df[c])]
    if nao_numericas:
        raise ValueError(f"Colunas nao numericas: {nao_numericas}")
    return colunas


def limites_iqr(serie: pd.Series, k: float = K_IQR) -> tuple[float, float]:
    """Cercas do criterio IQR: (Q1 - k*IQR, Q3 + k*IQR). Valores ausentes sao ignorados."""
    if not k >= 0:  # tambem rejeita NaN, que passaria por `k < 0`
        raise ValueError(f"k deve ser >= 0 (recebido: {k})")
    dados = serie.dropna()
    if dados.empty:
        raise ValueError("Nao ha valores para calcular os limites")
    q1, q3 = dados.quantile([0.25, 0.75])
    amplitude = q3 - q1
    return float(q1 - k * amplitude), float(q3 + k * amplitude)


def mascara_outliers(
    serie: pd.Series, criterio: str = "iqr", k: float = K_IQR, z: float = Z_LIMITE
) -> pd.Series:
    """Serie booleana (mesmo indice) marcando os outliers.

    `criterio="iqr"`: fora das cercas de `limites_iqr`. `criterio="z"`: |z-score| > `z`.
    Valores ausentes nunca sao outliers; serie constante nao tem outliers.
    """
    if criterio not in CRITERIOS:
        raise ValueError(f"criterio desconhecido: {criterio!r} (use {CRITERIOS})")

    if criterio == "iqr":
        inferior, superior = limites_iqr(serie, k)
        mascara = (serie < inferior) | (serie > superior)
    else:
        desvio = serie.std()
        if not desvio or np.isnan(desvio):
            return pd.Series(False, index=serie.index)
        mascara = ((serie - serie.mean()) / desvio).abs() > z
    return mascara.fillna(False).astype(bool)


def resumo_outliers(
    df: pd.DataFrame, colunas: Sequence[str], k: float = K_IQR, z: float = Z_LIMITE
) -> pd.DataFrame:
    """Uma linha por coluna: cercas IQR, outliers abaixo/acima, total, %, total pelo z-score e assimetria."""
    linhas = []
    for coluna in _validar_colunas(df, colunas):
        serie = df[coluna]
        inferior, superior = limites_iqr(serie, k)
        total = int(mascara_outliers(serie, "iqr", k=k).sum())
        linhas.append(
            {
                "variavel": coluna,
                "limite_inferior": inferior,
                "limite_superior": superior,
                "abaixo": int((serie < inferior).sum()),
                "acima": int((serie > superior).sum()),
                "total": total,
                "pct": total / serie.notna().sum() * 100,
                "total_z": int(mascara_outliers(serie, "z", z=z).sum()),
                "assimetria": float(serie.skew()),
            }
        )
    return pd.DataFrame(linhas).set_index("variavel")


def tratar(
    df: pd.DataFrame, colunas: Sequence[str], estrategia: str, k: float = K_IQR
) -> pd.DataFrame:
    """Devolve uma copia de `df` com os outliers (criterio IQR) das `colunas` tratados.

    - `manter`: nao altera nada.
    - `limitar`: corta os valores nas cercas do IQR (winsorizacao), sem perder linhas. Em coluna
      inteira a cerca e arredondada para dentro (piso na superior, teto na inferior), para a
      contagem continuar inteira.
    - `remover`: tira a linha inteira se qualquer uma das `colunas` tiver outlier.
    """
    if estrategia not in ESTRATEGIAS:
        raise ValueError(f"estrategia desconhecida: {estrategia!r} (use {ESTRATEGIAS})")
    colunas = _validar_colunas(df, colunas)

    if estrategia == "manter":
        return df.copy()
    if estrategia == "limitar":
        tratado = df.copy()
        for coluna in colunas:
            inferior, superior = limites_iqr(df[coluna], k)
            if pd.api.types.is_integer_dtype(df[coluna]):
                inferior, superior = math.ceil(inferior), math.floor(superior)
            tratado[coluna] = df[coluna].clip(inferior, superior)
        return tratado

    algum_outlier = pd.concat(
        [mascara_outliers(df[c], "iqr", k=k) for c in colunas], axis=1
    ).any(axis=1)
    return df.loc[~algum_outlier].copy()


def taxa_alvo_por_grupo(
    df: pd.DataFrame, colunas: Sequence[str], alvo: str, positivo: object, k: float = K_IQR
) -> pd.DataFrame:
    """Taxa (%) de `alvo == positivo` entre os outliers e entre os demais, por coluna.

    Mostra se ser outlier numa variavel esta associado a cancelar o cartao.
    """
    if alvo not in df.columns:
        raise ValueError(f"Coluna alvo inexistente: {alvo!r}")
    colunas = _validar_colunas(df, colunas)

    eh_positivo = df[alvo] == positivo
    linhas = []
    for coluna in colunas:
        outlier = mascara_outliers(df[coluna], "iqr", k=k)
        n_outliers = int(outlier.sum())
        taxa_outliers = eh_positivo[outlier].mean() * 100 if n_outliers else np.nan
        taxa_demais = eh_positivo[~outlier].mean() * 100 if (~outlier).any() else np.nan
        linhas.append(
            {
                "variavel": coluna,
                "n_outliers": n_outliers,
                "taxa_outliers": taxa_outliers,
                "taxa_demais": taxa_demais,
                "diferenca_pp": taxa_outliers - taxa_demais,
            }
        )
    return pd.DataFrame(linhas).set_index("variavel")
