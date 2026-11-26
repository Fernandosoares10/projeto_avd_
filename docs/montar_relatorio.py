# [IA] Claude Code – monta o relatorio.pdf a partir dos rascunhos de cada integrante (docs/rascunhos/) e das figuras
"""Junta as seções escritas pelo grupo em um único HTML e gera o relatorio.pdf na raiz do projeto.

Uso (a partir da raiz do projeto):
    python docs/montar_relatorio.py

Os textos vêm dos rascunhos em docs/rascunhos/ e das notas analíticas dos notebooks. Este script não escreve
análise: ele só organiza os textos do grupo na ordem do enunciado. Trechos ainda sem texto aparecem como PENDENTE.
O PDF é gerado com o Microsoft Edge em modo headless (instalado no Windows).
"""
import base64
import html
import json
import re
import subprocess
import zipfile
from pathlib import Path

import mistune

RAIZ = Path(__file__).resolve().parents[1]
RASCUNHOS = RAIZ / "docs" / "rascunhos"
OUT_COMUM = RAIZ / "out" / "parte_comum"
OUT_ESP = RAIZ / "out" / "parte_especifica"
SAIDA_HTML = RAIZ / "docs" / "rascunhos" / "relatorio_montado.html"
SAIDA_PDF = RAIZ / "relatorio.pdf"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

md = mistune.create_markdown(plugins=["table"])
contador_fig = 0


# ---------------------------------------------------------------- leitura das fontes
def secoes_markdown(arquivo: Path) -> dict[str, str]:
    """Separa um .md pelos títulos de nível 2 e 3 (## e ###): {título: corpo em markdown}."""
    secoes, titulo, corpo = {}, None, []
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{2,3} (.+)", linha)
        if m:
            if titulo:
                secoes[titulo] = "\n".join(corpo).strip()
            titulo, corpo = m.group(1).strip(), []
        elif titulo:
            corpo.append(linha)
    if titulo:
        secoes[titulo] = "\n".join(corpo).strip()
    return secoes


def paragrafos_markdown(arquivo: Path) -> list[str]:
    """Parágrafos de um .md (ignora títulos)."""
    texto = arquivo.read_text(encoding="utf-8")
    return [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip() and not p.lstrip().startswith("#")]


def nota_do_notebook(arquivo: Path) -> str:
    """Célula markdown '## Nota analítica' de um notebook, sem o título."""
    nb = json.loads(arquivo.read_text(encoding="utf-8"))
    for c in nb["cells"]:
        s = "".join(c["source"])
        if c["cell_type"] == "markdown" and s.startswith("## Nota anal"):
            return s.split("\n", 1)[1].strip()
    return ""


def docx_luis(arquivo: Path) -> list[tuple[str, str]]:
    """Lê o .docx do Luis: lista de (tipo, conteúdo), tipo em h1/h2/p/img/legenda."""
    z = zipfile.ZipFile(arquivo)
    xml = z.read("word/document.xml").decode("utf-8")
    rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    alvo_rel = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    itens = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        estilo = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        estilo = estilo.group(1) if estilo else ""
        texto = html.unescape("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))).strip()
        img = re.search(r'r:embed="([^"]+)"', p)
        if img:
            dados = z.read("word/" + alvo_rel[img.group(1)])
            itens.append(("img", base64.b64encode(dados).decode()))
        elif estilo in ("Title", "Subtitle") or not texto:
            continue
        elif texto.startswith("Observação para a montagem final"):
            continue
        elif estilo == "Heading1":
            itens.append(("h1", re.sub(r"^\d+\s+", "", texto)))
        elif estilo == "Heading2":
            itens.append(("h2", texto))
        elif texto.startswith("Figura"):
            itens.append(("legenda", re.sub(r"^Figura \d+:\s*", "", texto)))
        else:
            itens.append(("p", texto))
    return itens


# ---------------------------------------------------------------- blocos de HTML
def figura(caminho_ou_b64: str | Path, legenda: str) -> str:
    global contador_fig
    contador_fig += 1
    if isinstance(caminho_ou_b64, Path):
        b64 = base64.b64encode(caminho_ou_b64.read_bytes()).decode()
    else:
        b64 = caminho_ou_b64
    return (f'<figure><img src="data:image/png;base64,{b64}">'
            f"<figcaption>Figura {contador_fig}: {html.escape(legenda)}</figcaption></figure>")


def pendente(o_que: str) -> str:
    return f'<p class="pendente"><b>PENDENTE:</b> {html.escape(o_que)}</p>'


def bloco_md(texto: str) -> str:
    return md(texto) if texto.strip() else ""


def luis_html(itens: list[tuple[str, str]], h1_incluir: set[str], com_titulo: bool = True) -> str:
    """Converte as seções escolhidas do docx do Luis em HTML (subtítulos viram h3)."""
    partes, ativo, img_pendente = [], False, None
    for tipo, conteudo in itens:
        if tipo == "h1":
            ativo = conteudo in h1_incluir
            if ativo and com_titulo:
                partes.append(f"<h3>{html.escape(conteudo)}</h3>")
            continue
        if not ativo:
            continue
        if tipo == "h2":
            partes.append(f"<h4>{html.escape(conteudo)}</h4>")
        elif tipo == "p":
            # rotulos em negrito do Word chegam como "**Rotulo: texto" sem o fechamento
            partes.append(md(re.sub(r"^\*\*([^*:]+:)\s*", r"**** ", conteudo)))
        elif tipo == "img":
            img_pendente = conteudo
        elif tipo == "legenda" and img_pendente:
            partes.append(figura(img_pendente, conteudo))
            img_pendente = None
    return "\n".join(partes)


# ---------------------------------------------------------------- montagem
def montar() -> str:
    luis = docx_luis(RASCUNHOS / "relatorio_e10_eda.docx")
    pedro = secoes_markdown(RASCUNHOS / "relatorio_pedro_relacoes_visualizacoes.md")
    adrian = secoes_markdown(RASCUNHOS / "relatorio_adrian_passada1_outliers.md")
    fernando = paragrafos_markdown(RASCUNHOS / "relatorio_fernando_passada2_eda_estrutural.md")
    f_mcar = next(p for p in fernando if p.startswith("No nosso projeto"))
    f_tabelas = next(p for p in fernando if p.startswith("Para analisar isso"))
    f_padron = next(p for p in fernando if p.startswith("Outro ponto importante"))
    f_metricas = next(p for p in fernando if p.startswith("Sobre as métricas"))
    f_pca = next(p for p in fernando if p.startswith("Por último"))

    extras = {}
    arquivo_extras = RASCUNHOS / "relatorio_fernando_textos_finais.md"
    if arquivo_extras.exists():
        extras = secoes_markdown(arquivo_extras)

    def extra(titulo: str, descricao: str) -> str:
        return bloco_md(extras[titulo]) if extras.get(titulo, "").strip() else pendente(descricao)

    nota_viz1 = nota_do_notebook(RAIZ / "src/parte_especifica/viz_exploratoria_1.ipynb")
    nota_viz4 = nota_do_notebook(RAIZ / "src/parte_especifica/viz_exploratoria_4.ipynb")
    nota_expl2 = nota_do_notebook(RAIZ / "src/parte_especifica/viz_explanatoria_2.ipynb")
    notas_pedro = pedro.get("Notas analíticas: Visualização Exploratória 3 e Visualização Explanatória 1", "")
    p_exp3 = next((p for p in notas_pedro.split("\n\n") if "Exploratória 3" in p), "")
    p_expl1 = next((p for p in notas_pedro.split("\n\n") if "Explanatória 1" in p), "")

    h = []
    h.append("""<section class="capa">
<h1>Projeto Final: Agrupamento, EDA e Dashboard Interativo</h1>
<p class="sub">Análise e Visualização de Dados (AVD) · CESAR School · 2026.2</p>
<p><b>Integrantes:</b> Fernando Soares da Silva, Luis Guilherme Lauria, Pedro Loureiro Galvão Guerra e Adrian Michael de Araujo</p>
<p><b>Datasets:</b> Obesity (UCI 544) na Parte Comum; Credit Card Customers (BankChurners, Kaggle) na Parte Específica</p>
<p><b>Repositório:</b> github.com/Fernandosoares10/projeto_avd_</p>
<p><b>Data:</b> 26/11/2026</p>
</section>""")

    # ------------------------------ Parte Comum
    h.append('<h1 class="parte">Parte Comum: Obesity</h1>')
    h.append("<h2>1. Análise exploratória (EDA)</h2>")
    h.append(luis_html(luis, {"Estrutura do Obesity", "Distribuições do Obesity", "Outliers"}))
    h.append("<h3>Relações entre as variáveis e com a classe</h3>")
    h.append(figura(OUT_COMUM / "eda_relacional_correlacao_comum.png", "Correlação entre as variáveis numéricas do Obesity."))
    h.append(figura(OUT_COMUM / "eda_relacional_peso_altura_classe.png", "Peso e altura por classe de NObeyesdad."))

    h.append("<h2>2. Padronização</h2>")
    h.append(md(f_padron.replace("Outro ponto importante é a padronização no K-Means. ", "A padronização é importante no K-Means. ")))

    h.append("<h2>3. K-Means: Passada 1 (k livre)</h2>")
    h.append(bloco_md(adrian.get("Passada 1: escolha do k e resultados", "")))
    h.append(figura(OUT_COMUM / "passada1_cotovelo.png", "Método do Cotovelo (inércia para k de 2 a 10)."))
    h.append(figura(OUT_COMUM / "passada1_clusters_pca.png", "Passada 1: clusters projetados em 2 componentes principais."))

    h.append("<h2>4. K-Means: Passada 2 (k fixo = 7)</h2>")
    h.append(extra("Passada 2: escolha das variáveis e matriz de confusão",
                   "texto do Fernando sobre as 8 variáveis numéricas, Height/Weight e a leitura da matriz de confusão."))
    h.append(md(f_metricas))
    h.append(md(f_pca))
    h.append(figura(OUT_COMUM / "passada2_clusters_pca.png", "Passada 2: clusters do K-Means e classes reais na mesma projeção PCA."))
    h.append(figura(OUT_COMUM / "passada2_matriz_confusao.png", "Passada 2: matriz de confusão em % por linha (cada classe real soma 100%), com a quantidade de pessoas entre parênteses."))

    h.append("<h2>5. Discussão crítica</h2>")
    h.append("<h3>Passada 1 x Passada 2</h3>")
    h.append(bloco_md(adrian.get("Discussão crítica: qual passada gerou grupos mais coerentes?", "")))
    h.append("<h3>Granularidade das classes</h3>")
    h.append(bloco_md(adrian.get("Granularidade das classes", "")))
    h.append(bloco_md(pedro.get("Granularidade das classes no dataset Obesity (Parte Comum)", "")))

    # ------------------------------ Parte Específica
    h.append('<h1 class="parte">Parte Específica: BankChurners</h1>')
    h.append("<h2>6. Pergunta de pesquisa e público-alvo</h2>")
    h.append(extra("Pergunta de pesquisa", "pergunta de pesquisa (hipótese) do grupo."))
    h.append(extra("Público-alvo", "público-alvo da comunicação e por que a linguagem foi escolhida para ele."))

    h.append("<h2>7. Análise exploratória (EDA)</h2>")
    h.append("<h3>Estrutura e qualidade dos dados</h3>")
    h.append(extra("Classificação das variáveis", "classificação das variáveis do BankChurners."))
    h.append("<h3>Valores ausentes (Unknown)</h3>")
    h.append(md(f_mcar))
    h.append(md(f_tabelas))
    h.append(extra("Mecanismo de ausência", "mecanismo de ausência de Education_Level, Marital_Status e Income_Category."))
    h.append(extra("Justificativa do tratamento", "justificativa de manter Unknown como categoria própria."))
    h.append(luis_html(luis, {"Distribuições do BankChurners"}))
    h.append("<h3>Relações e análise multivariada</h3>")
    h.append(bloco_md(pedro.get("EDA relacional e multivariada do BankChurners", "")))
    h.append(figura(OUT_ESP / "eda_relacional_correlacao.png", "Correlação entre as variáveis numéricas do BankChurners."))
    h.append("<h4>Variáveis derivadas</h4>")
    h.append(bloco_md(pedro.get("Documentação e verificação das variáveis derivadas", "")))
    h.append("<h3>Outliers</h3>")
    for titulo in ("Os outliers são erros ou clientes reais?", "Ser outlier tem relação com cancelar?", "Tratamento adotado"):
        h.append(f"<h4>{titulo}</h4>")
        h.append(bloco_md(adrian.get(titulo, "")))

    h.append("<h2>8. Visualizações e notas analíticas</h2>")
    h.append("<h3>Visualização exploratória 1: boxplot de Total_Trans_Amt por situação do cliente</h3>")
    h.append(figura(OUT_ESP / "viz_exploratoria_1_boxplot_trans_amt.png", "Valor total transacionado em 12 meses: quem ficou x quem cancelou."))
    h.append(bloco_md(nota_viz1))
    h.append("<h3>Visualização exploratória 2: violino de Total_Trans_Ct por situação do cliente</h3>")
    h.append(luis_html(luis, {"Visualização exploratória 2"}, com_titulo=False))
    h.append("<h3>Visualização exploratória 3: heatmap de contatos x meses de inatividade</h3>")
    h.append(figura(OUT_ESP / "viz_exploratoria_3_heatmap_contatos_inatividade.png", "Taxa de cancelamento por contatos e meses de inatividade."))
    h.append(bloco_md(p_exp3))
    h.append("<h3>Visualização exploratória 4: dispersão de transações x valor transacionado</h3>")
    h.append(figura(OUT_ESP / "viz_exploratoria_4_dispersao_trans_ct_amt.png", "Quantidade de transações x valor transacionado, por situação do cliente."))
    h.append(bloco_md(nota_viz4))
    h.append("<h3>Visualização explanatória 1: cancelamento por faixa de transações e queda no 4º trimestre</h3>")
    h.append(figura(OUT_ESP / "viz_explanatoria_1_churn_transacoes_queda.png", "Taxa de cancelamento por faixa de transações e ritmo no Q4."))
    h.append(bloco_md(p_expl1))
    h.append("<h3>Visualização explanatória 2: cancelamento por número de produtos</h3>")
    h.append(figura(OUT_ESP / "viz_explanatoria_2_barras_produtos.png", "Taxa de cancelamento por número de produtos do banco."))
    h.append(bloco_md(nota_expl2))

    h.append("<h2>9. Storytelling: da exploratória à explanatória</h2>")
    h.append(extra("Storytelling", "o que a exploração mostrou, por que a mensagem importa para o público e quais "
                                   "atributos pré-atentivos (cor, posição, título) foram usados para destacá-la."))

    h.append("<h2>10. Dashboard em Streamlit</h2>")
    h.append(md("O dashboard (`streamlit run src/parte_especifica/dashboard.py`) tem seis páginas: Início, Qualidade "
                "dos dados, Distribuições, Relações, Outliers e uma página da Parte Comum com o K-Means do Obesity."))
    h.append(bloco_md(pedro.get("Página 3 do dashboard (`Relacoes`)", "")))

    h.append("<h2>11. Resposta à pergunta de pesquisa</h2>")
    h.append(extra("Resposta à pergunta de pesquisa", "resposta à pergunta de pesquisa com base nas visualizações explanatórias."))
    return "\n".join(h)


ESTILO = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #111; }
.capa { page-break-after: always; padding-top: 70mm; }
.capa h1 { font-size: 22pt; } .capa .sub { font-size: 12pt; color: #444; }
h1.parte { font-size: 18pt; page-break-before: always; border-bottom: 2px solid #333; }
h2 { font-size: 14pt; margin-top: 20px; } h3 { font-size: 12pt; margin-top: 14px; } h4 { font-size: 11pt; }
p { text-align: justify; }
figure { margin: 10px 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 120mm; }
figcaption { font-size: 9pt; color: #444; margin-top: 4px; }
code { font-family: Consolas, monospace; font-size: 9.5pt; }
table { border-collapse: collapse; } th, td { border: 1px solid #aaa; padding: 3px 6px; }
.pendente { background: #fff2a8; padding: 6px; border-left: 4px solid #d4a000; }
"""


def main() -> None:
    corpo = montar()
    pagina = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório</title>'
              f"<style>{ESTILO}</style></head><body>{corpo}</body></html>")
    SAIDA_HTML.write_text(pagina, encoding="utf-8")
    subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={SAIDA_PDF}", SAIDA_HTML.as_uri()], check=True, capture_output=True)
    pendentes = corpo.count('class="pendente"')
    print(f"Gerado {SAIDA_PDF} ({contador_fig} figuras, {pendentes} trechos PENDENTES)")


if __name__ == "__main__":
    main()
