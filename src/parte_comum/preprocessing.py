# [IA] Claude Code – carga do Obesity e padronização z-score (Passada 1)
"""Carga e padronização do dataset Obesity (UCI 544)."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

ALVO = "NObeyesdad"

# Variáveis numéricas usadas no K-Means (as demais são categóricas).
NUMERICAS: tuple[str, ...] = (
    "Age",
    "Height",
    "Weight",
    "FCVC",
    "NCP",
    "CH2O",
    "FAF",
    "TUE",
)


def carregar_obesity(caminho: str | Path) -> pd.DataFrame:
    """Lê o CSV do Obesity. Levanta FileNotFoundError se o arquivo não existir."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(f"Dataset não encontrado: {caminho}")
    return pd.read_csv(caminho)


def padronizar(df: pd.DataFrame, colunas: Sequence[str]) -> pd.DataFrame:
    """Devolve as `colunas` com média 0 e desvio 1 (z-score), sem alterar `df`.

    Coluna constante vira 0 (sem NaN). Levanta ValueError se alguma coluna
    não existir ou não for numérica.
    """
    colunas = list(colunas)
    ausentes = [c for c in colunas if c not in df.columns]
    if ausentes:
        raise ValueError(f"Colunas inexistentes: {ausentes}")

    nao_numericas = [c for c in colunas if not pd.api.types.is_numeric_dtype(df[c])]
    if nao_numericas:
        raise ValueError(f"Colunas não numéricas: {nao_numericas}")

    com_ausentes = [c for c in colunas if df[c].isna().any()]
    if com_ausentes:
        raise ValueError(f"Colunas com valores ausentes: {com_ausentes}")

    valores = StandardScaler().fit_transform(df[colunas])
    return pd.DataFrame(valores, columns=colunas, index=df.index)
