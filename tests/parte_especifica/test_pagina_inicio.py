# [IA] Claude Code – testes da pagina inicial (exportacao do relatorio pelo dashboard)
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PASTA_APP = Path(__file__).resolve().parents[2] / "src" / "parte_especifica"
if str(PASTA_APP) not in sys.path:
    sys.path.insert(0, str(PASTA_APP))


@pytest.fixture
def app() -> AppTest:
    return AppTest.from_file(str(PASTA_APP / "app_pages" / "inicio.py"), default_timeout=60).run()


def test_pagina_inicial_abre_sem_erros(app):
    assert not app.exception


def test_pagina_inicial_oferece_download_do_relatorio(app):
    botoes = app.get("download_button")
    assert any("Baixar relatorio completo" in b.proto.label for b in botoes)
