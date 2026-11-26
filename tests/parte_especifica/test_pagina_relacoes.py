# [IA] Claude Code – testes (TDD) da pagina Relacoes do dashboard: a explanatoria 2 fica junto da explanatoria 1
import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

PASTA_APP = Path(__file__).resolve().parents[2] / "src" / "parte_especifica"
PAGINA = PASTA_APP / "app_pages" / "3_relacoes.py"

# As paginas importam `dados` e `taxas` direto: o Streamlit poe a pasta do dashboard.py no sys.path.
if str(PASTA_APP) not in sys.path:
    sys.path.insert(0, str(PASTA_APP))


def _metrica(app: AppTest, rotulo: str) -> str:
    return next(m.value for m in app.metric if m.label == rotulo)


@pytest.fixture(scope="module")
def app() -> AppTest:
    return AppTest.from_file(str(PAGINA), default_timeout=120).run()


def test_pagina_abre_sem_erros(app):
    assert not app.exception


def test_pagina_tem_a_explanatoria_2(app):
    titulos = [s.value for s in app.subheader]

    assert any("Visualizacao explanatoria 2" in t for t in titulos)


def test_explanatoria_2_mostra_as_taxas_reais_por_numero_de_produtos(app):
    assert _metrica(app, "Cancelam com 1 ou 2 produtos") == "26.9%"
    assert _metrica(app, "Cancelam com 4 a 6 produtos") == "11.4%"
    assert _metrica(app, "Diferenca entre os dois grupos") == "2.4x"


def test_explanatoria_2_nota_traz_as_taxas_e_o_peso_do_grupo(app):
    textos = " ".join(m.value for m in app.markdown)

    assert "26,9%" in textos and "11,4%" in textos and "2,4" in textos
    assert "21,3%" in textos and "35,6%" in textos


def test_explanatoria_2_usa_o_titulo_do_grupo(app):
    titulos = [c.proto.spec for c in app.get("plotly_chart")]
    assert any("Menos Produtos Contratados" in t for t in titulos)
