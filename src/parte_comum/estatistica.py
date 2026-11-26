# [IA] Claude Code – testes estatisticos (qui-quadrado, Kruskal-Wallis e Mann-Whitney) so com numpy e pandas
"""Testes estatísticos usados na EDA relacional, sem scipy (fora da lista de bibliotecas permitidas).

Os cálculos seguem as fórmulas clássicas, com as mesmas correções usadas por padrão em bibliotecas estatísticas:
- qui-quadrado: correção de continuidade de Yates quando a tabela tem 1 grau de liberdade (2 x 2);
- Kruskal-Wallis e Mann-Whitney: correção para empates; Mann-Whitney usa aproximação normal com correção de
  continuidade (adequada para amostras grandes, como as deste projeto).
"""
import math

import numpy as np
import pandas as pd


def _gama_incompleta_superior_regularizada(a: float, x: float) -> float:
    """Q(a, x) = Γ(a, x) / Γ(a), por série (x < a + 1) ou fração contínua (x >= a + 1)."""
    if x <= 0:
        return 1.0
    log_prefixo = -x + a * math.log(x) - math.lgamma(a)
    if x < a + 1:
        termo = soma = 1.0 / a
        ap = a
        for _ in range(10_000):
            ap += 1
            termo *= x / ap
            soma += termo
            if abs(termo) < abs(soma) * 1e-15:
                break
        return max(0.0, 1.0 - soma * math.exp(log_prefixo))
    # fracao continua de Lentz
    minimo = 1e-300
    b = x + 1 - a
    c = 1 / minimo
    d = 1 / b
    h = d
    for i in range(1, 10_000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = minimo if abs(d) < minimo else d
        c = b + an / c
        c = minimo if abs(c) < minimo else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return min(1.0, math.exp(log_prefixo) * h)


def p_valor_qui_quadrado(estatistica: float, graus_liberdade: int) -> float:
    """P(X >= estatistica) para X ~ qui-quadrado com `graus_liberdade`."""
    return _gama_incompleta_superior_regularizada(graus_liberdade / 2, estatistica / 2)


def p_valor_normal_bilateral(z: float) -> float:
    """P(|Z| >= |z|) para Z ~ Normal(0, 1)."""
    return min(1.0, math.erfc(abs(z) / math.sqrt(2)))


def qui_quadrado_contingencia(tabela: pd.DataFrame) -> tuple[float, float, int]:
    """Teste qui-quadrado de independência numa tabela de contingência: (qui2, p-valor, graus de liberdade)."""
    observado = np.asarray(tabela, dtype=float)
    if observado.ndim != 2 or min(observado.shape) < 2:
        raise ValueError("A tabela precisa ter pelo menos 2 linhas e 2 colunas")
    total = observado.sum()
    esperado = observado.sum(axis=1, keepdims=True) * observado.sum(axis=0, keepdims=True) / total
    graus = (observado.shape[0] - 1) * (observado.shape[1] - 1)
    diferenca = observado - esperado
    if graus == 1:  # correcao de Yates
        diferenca = np.sign(diferenca) * np.minimum(np.abs(diferenca), 0.5)
        diferenca = (observado - esperado) - diferenca
    qui2 = float(((diferenca ** 2) / esperado).sum())
    return qui2, p_valor_qui_quadrado(qui2, graus), graus


def _soma_empates(valores: np.ndarray) -> float:
    """Soma de (t³ - t) sobre os grupos de valores empatados."""
    _, contagens = np.unique(valores, return_counts=True)
    return float(((contagens ** 3) - contagens).sum())


def kruskal_wallis(*grupos) -> tuple[float, float]:
    """Teste de Kruskal-Wallis com correção de empates: (H, p-valor)."""
    grupos = [np.asarray(g, dtype=float) for g in grupos]
    if len(grupos) < 2 or any(len(g) == 0 for g in grupos):
        raise ValueError("São necessários pelo menos 2 grupos não vazios")
    todos = np.concatenate(grupos)
    n = len(todos)
    postos = pd.Series(todos).rank(method="average").to_numpy()
    h, inicio = 0.0, 0
    for g in grupos:
        h += postos[inicio:inicio + len(g)].sum() ** 2 / len(g)
        inicio += len(g)
    h = 12 / (n * (n + 1)) * h - 3 * (n + 1)
    correcao = 1 - _soma_empates(todos) / (n ** 3 - n)
    h = h / correcao if correcao > 0 else h
    return float(h), p_valor_qui_quadrado(h, len(grupos) - 1)


def mann_whitney(x, y) -> tuple[float, float]:
    """Teste de Mann-Whitney bilateral (aproximação normal, correção de empates e de continuidade): (U de x, p-valor)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        raise ValueError("Os dois grupos precisam ter valores")
    todos = np.concatenate([x, y])
    n = n1 + n2
    postos = pd.Series(todos).rank(method="average").to_numpy()
    u1 = postos[:n1].sum() - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    media = n1 * n2 / 2
    desvio = math.sqrt(n1 * n2 / 12 * ((n + 1) - _soma_empates(todos) / (n * (n - 1))))
    if desvio == 0:
        return float(u1), 1.0
    z = (max(u1, u2) - media - 0.5) / desvio
    return float(u1), p_valor_normal_bilateral(z)
