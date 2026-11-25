# [IA] Claude Code – testes (TDD) da pagina da Parte Comum (Obesity: K-Means) com o AppTest do Streamlit
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PASTA_APP = Path(__file__).resolve().parents[2] / "src" / "parte_especifica"
PAGINA = PASTA_APP / "app_pages" / "5_parte_comum.py"

# Valores reais do K-Means com k = 7 e semente 42 (iguais aos da Passada 2 do notebook do grupo).
ACURACIA_K7 = "38.8%"

if str(PASTA_APP) not in sys.path:
    sys.path.insert(0, str(PASTA_APP))


def _metrica(app: AppTest, rotulo: str) -> str:
    return next(m.value for m in app.metric if m.label == rotulo)


@pytest.fixture
def app() -> AppTest:
    return AppTest.from_file(str(PAGINA), default_timeout=90).run()


def test_pagina_abre_sem_erros(app):
    assert not app.exception


def test_pagina_mostra_o_tamanho_do_dataset(app):
    assert _metrica(app, "Pessoas") == "2.111"
    assert _metrica(app, "Variaveis no K-Means") == "8"
    assert _metrica(app, "Classes reais") == "7"


def test_k_padrao_e_sete_e_reproduz_a_acuracia_da_passada_2(app):
    assert app.slider(key="pc_k").value == 7
    assert _metrica(app, "Acuracia") == ACURACIA_K7


def test_mudar_o_k_recalcula_os_grupos_e_as_metricas(app):
    app.slider(key="pc_k").set_value(3).run()

    assert not app.exception
    assert _metrica(app, "Grupos (k)") == "3"
    assert _metrica(app, "Acuracia") != ACURACIA_K7


def _matriz_de_confusao(app: AppTest):
    return next(df.value for df in app.dataframe if df.value.shape == (7, 7))


def test_matriz_de_confusao_conta_todas_as_pessoas_e_a_diagonal_da_a_acuracia(app):
    matriz = _matriz_de_confusao(app).to_numpy()

    assert matriz.sum() == 2111
    assert round(matriz.trace() / 2111 * 100, 1) == 38.8  # mesma acuracia mostrada na metrica


def test_aviso_lista_so_a_classe_sem_grupo_com_k_sete(app):
    # Com k = 7, so Overweight_Level_II nao vira classe majoritaria de nenhum cluster.
    assert len(app.warning) == 1
    aviso = app.warning[0].value
    assert "Overweight_Level_II" in aviso
    assert "Obesity_Type_I" not in aviso and "Normal_Weight" not in aviso
