# [IA] Claude Code – testes (TDD) da pagina Outliers do dashboard, com o AppTest do Streamlit
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PASTA_APP = Path(__file__).resolve().parents[2] / "src" / "parte_especifica"
PAGINA = PASTA_APP / "app_pages" / "4_outliers.py"
TOTAL_CLIENTES = 10127
OUTLIERS_TOTAL_TRANS_AMT = 896  # pelo criterio IQR com k = 1,5
CLIENTES_COM_OUTLIER = 3326      # com ao menos um outlier em qualquer variavel (k = 1,5)
ASSIMETRIA_ORIGINAL = "2.04"     # Total_Trans_Amt
ASSIMETRIA_LIMITADA = "0.84"     # Total_Trans_Amt depois de limitar nas cercas do IQR

# As paginas importam `dados` e `outliers` direto: o Streamlit poe a pasta do dashboard.py no sys.path.
if str(PASTA_APP) not in sys.path:
    sys.path.insert(0, str(PASTA_APP))


def _numero(texto: str) -> int:
    """'10.127' (formato pt-BR dos st.metric) -> 10127."""
    return int(texto.replace(".", ""))


def _metrica(app: AppTest, rotulo: str) -> str:
    return next(m.value for m in app.metric if m.label == rotulo)


@pytest.fixture
def app() -> AppTest:
    return AppTest.from_file(str(PAGINA), default_timeout=60).run()


def test_pagina_abre_sem_erros(app):
    assert not app.exception


def test_pagina_mostra_clientes_com_outlier_e_clientes_apos_tratamento(app):
    assert _numero(_metrica(app, "Clientes com pelo menos um outlier")) == CLIENTES_COM_OUTLIER
    assert _numero(_metrica(app, "Clientes apos o tratamento")) == TOTAL_CLIENTES


def test_aumentar_o_multiplicador_k_reduz_os_clientes_com_outlier(app):
    com_k_padrao = _numero(_metrica(app, "Clientes com pelo menos um outlier"))

    app.slider(key="out_k").set_value(3.0).run()

    assert not app.exception
    assert _numero(_metrica(app, "Clientes com pelo menos um outlier")) < com_k_padrao


def test_remover_tira_os_clientes_outliers_da_variavel(app):
    app.selectbox(key="out_var").set_value("Total_Trans_Amt").run()
    app.radio(key="out_estrategia").set_value("remover").run()

    assert not app.exception
    assert _numero(_metrica(app, "Clientes apos o tratamento")) == TOTAL_CLIENTES - OUTLIERS_TOTAL_TRANS_AMT


def test_limitar_nao_perde_nenhum_cliente(app):
    app.selectbox(key="out_var").set_value("Total_Trans_Amt").run()
    app.radio(key="out_estrategia").set_value("limitar").run()

    assert not app.exception
    assert _numero(_metrica(app, "Clientes apos o tratamento")) == TOTAL_CLIENTES
    # limitar de fato mexe nos valores: a assimetria cai (um limitar que nao fizesse nada manteria 2.04)
    assert _metrica(app, "Assimetria") == ASSIMETRIA_LIMITADA


def test_manter_nao_muda_a_assimetria(app):
    app.selectbox(key="out_var").set_value("Total_Trans_Amt").run()

    assert _metrica(app, "Assimetria") == ASSIMETRIA_ORIGINAL


def test_variavel_sem_outliers_nao_quebra_a_pagina_nem_remove_clientes(app):
    app.selectbox(key="out_var").set_value("Dependent_count").run()
    app.radio(key="out_estrategia").set_value("remover").run()

    assert not app.exception
    assert _numero(_metrica(app, "Clientes apos o tratamento")) == TOTAL_CLIENTES
    assert any("nao tem outliers" in aviso.value for aviso in app.info)


def test_grafico_de_cancelamento_nao_mostra_variaveis_com_poucos_outliers(app):
    # Customer_Age e Total_Trans_Ct tem so 2 outliers: uma taxa de 0% sobre 2 clientes nao significa nada.
    legendas = " ".join(c.value for c in app.caption)

    assert "poucos outliers" in legendas
