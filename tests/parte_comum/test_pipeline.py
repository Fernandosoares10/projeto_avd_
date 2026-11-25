# [IA] Claude Code – teste de integração do pipeline da Passada 1
"""Teste de integração: pipeline completo da Passada 1 com o CSV real."""

from pathlib import Path

from parte_comum.avaliacao import avaliar
from parte_comum.clustering import ajustar_kmeans, aplicar_mapa, mapear_clusters
from parte_comum.preprocessing import ALVO, NUMERICAS, carregar_obesity, padronizar

CAMINHO_OBESITY = (
    Path(__file__).resolve().parents[2] / "data" / "parte_comum" / "obesity.csv"
)


def test_pipeline_passada1_roda_de_ponta_a_ponta_com_dados_reais():
    df = carregar_obesity(CAMINHO_OBESITY)

    X = padronizar(df, NUMERICAS)
    labels = ajustar_kmeans(X, k=7)
    mapa = mapear_clusters(labels, df[ALVO])
    resultado = avaliar(df[ALVO], aplicar_mapa(labels, mapa))

    assert len(labels) == len(df)
    assert set(mapa) == set(range(7))
    assert int(resultado["matriz_confusao"].to_numpy().sum()) == len(df)
    # Acima do acaso entre 7 classes (~14%); o valor real com seed 42 é ≈ 39%.
    assert resultado["acuracia"] > 0.30
