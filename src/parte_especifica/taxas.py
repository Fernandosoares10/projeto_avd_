# [IA] Claude Code – taxas de cancelamento por categoria e por recorte (visualizacoes 4 e explanatoria 2)
"""Calculos de taxa (%) sem dependencia do Streamlit, usados pelos notebooks e pela pagina Outliers."""
import numpy as np
import pandas as pd


def _validar_colunas(df: pd.DataFrame, *colunas: str) -> None:
    for coluna in colunas:
        if coluna not in df.columns:
            raise ValueError(f"Coluna inexistente: {coluna!r}")


def taxa_por_categoria(df: pd.DataFrame, coluna: str, alvo: str, positivo: object) -> pd.DataFrame:
    """Por categoria de `coluna`: n (clientes), positivos (`alvo == positivo`) e taxa (%).

    Categorias ausentes (NaN) ficam de fora. O resultado vem ordenado pela categoria.
    """
    _validar_colunas(df, coluna, alvo)
    grupos = (df[alvo] == positivo).groupby(df[coluna])
    tabela = pd.DataFrame({"n": grupos.size(), "positivos": grupos.sum()}).astype(int)
    tabela["taxa"] = tabela["positivos"] / tabela["n"] * 100
    return tabela.sort_index()


def taxa_do_recorte(df: pd.DataFrame, recorte: pd.Series, alvo: str, positivo: object) -> float:
    """Percentual de `alvo == positivo` dentro das linhas marcadas em `recorte` (NaN se o recorte for vazio)."""
    _validar_colunas(df, alvo)
    if len(recorte) != len(df):
        raise ValueError(f"recorte ({len(recorte)}) e df ({len(df)}) tem tamanhos diferentes")
    marcadas = np.asarray(recorte, dtype=bool)
    if not marcadas.any():
        return float("nan")
    return float((df.loc[marcadas, alvo] == positivo).mean() * 100)
