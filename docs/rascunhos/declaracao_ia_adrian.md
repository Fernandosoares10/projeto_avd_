# Declaração de uso de IA: parte de Adrian Michael de Araujo (rascunho)

> **Rascunho para o grupo.** A declaração oficial é `docs/DECLARACAO_IA.pdf`, assinada por todos. Este texto cobre
> só a parte do Adrian e deve ser adaptado ao modelo exigido pelo enunciado. Os campos entre colchetes e as caixas
> `[ ]` precisam ser preenchidos ou marcados por quem assina.

## 1. Identificação

- **Integrante:** Adrian Michael de Araujo
- **Disciplina:** Análise e Visualização de Dados (AVD), CESAR School, 2026.2
- **Projeto:** Agrupamento, EDA e Dashboard Interativo (Obesity e BankChurners)
- **Data:** 24/11/2026

## 2. Ferramenta utilizada

- **Claude Code** (assistente de programação da Anthropic, executado no terminal), com o modelo Claude Sonnet 5.5.
- Dentro do Claude Code, uma segunda instância do Claude foi usada **só para revisão de código** (agente
  `python-reviewer`). Ela leu o código e apontou problemas, mas não escreveu nem alterou arquivos.

## 3. Para que a IA foi usada

| Entregável | O que a IA fez |
|---|---|
| Passada 1 (K-Means de 2 a 10, cotovelo, PCA, mapeamento cluster → classe, métricas) | Escreveu as funções em `src/parte_comum/` (padronização, K-Means, mapeamento, avaliação, gráficos), os testes em `tests/parte_comum/` e o notebook `kmeans_passada1.ipynb` |
| Outliers do BankChurners | Escreveu `src/parte_especifica/outliers.py`, os testes e o notebook `eda_outliers.ipynb`, incluindo a **proposta** de tratamento |
| Visualização exploratória 4 e explanatória 2 | Escreveu `taxas.py`, os notebooks `viz_exploratoria_4.ipynb` e `viz_explanatoria_2.ipynb`, os gráficos e as notas analíticas |
| Dashboard | Escreveu as páginas `4_outliers.py` e `5_parte_comum.py` e os testes automáticos delas |
| Relatório | Escreveu o **rascunho** da seção "Passada 1 e outliers" (`docs/rascunhos/relatorio_adrian_passada1_outliers.md`) |
| Apoio | Configurou o `pytest`, ajustou o README (nome, notebooks, testes) e baixou o dataset Obesity do UCI (depois substituído pelo arquivo do grupo, idêntico) |
| Revisão | Levantou números nos dados para fundamentar as opções de visualização e para conferir os textos |

Todo código gerado com apoio de IA está marcado, como pede o README do grupo, com o comentário
`# [IA] Claude Code – <finalidade>` (nos arquivos `.py`, nos testes e em cada célula de código dos notebooks).

## 4. O que foi decisão humana

- A escolha do dataset da Parte Comum (**Obesity**).
- A escolha dos tipos de visualização: **exploratória 4 = dispersão** e **explanatória 2 = produtos do banco**, entre
  opções que a IA apresentou com números dos dados.
- A aprovação de cada commit e de cada publicação no GitHub (a IA só publicou depois de confirmação).
- A aprovação final do conteúdo, que depende do grupo (ver seção 6).

A IA **não** escreveu a pergunta de pesquisa nem o público-alvo do projeto.

## 5. Como o resultado foi verificado

- **Testes antes do código (TDD):** os testes foram escritos primeiro e vistos falhando antes da implementação.
  A suíte tem 107 testes automáticos, todos passando.
- **Revisão independente:** cada bloco de código passou por uma revisão feita por outra instância da IA, e os
  problemas encontrados foram corrigidos.
- **Conferência dos números:** os valores citados nas notas analíticas e no rascunho do relatório foram
  recalculados diretamente dos dados por duas vias (o código e o revisor).
- **Execução do zero:** os 9 notebooks foram executados e o dashboard foi aberto no navegador em uma cópia limpa
  do repositório.

## 6. Limites e pontos que o grupo deve conferir

- **O texto das notas analíticas e do relatório foi escrito pela IA.** Os números vêm dos dados, mas a redação e as
  interpretações precisam ser lidas e assumidas por quem assina.
- **Decisões propostas pela IA, ainda não aprovadas pelo grupo:** adotar k = 7 na Passada 1 (o resultado coincide
  com o da Passada 2) e manter os outliers sem removê-los.
- **Afirmação sobre o dataset não conferida:** a frase de que as classes do Obesity são definidas a partir do IMC
  vem do conhecimento da IA e deve ser verificada na descrição do UCI (544).
- **Associação, não causa:** as notas das visualizações 4 e explanatória 2 descrevem associações nos dados e não
  provam relação de causa.

## 7. Confirmação do integrante

Marque o que de fato foi feito:

- [ ] Li o código e os textos produzidos com apoio de IA na minha parte.
- [ ] Entendo o que cada parte faz e consigo explicá-la.
- [ ] Executei os notebooks e o dashboard e conferi os resultados principais.
- [ ] Concordo com as decisões da seção 6 ou levei cada uma ao grupo.

**Assinatura:** [preencher]
