# Projeto Final AVD: Agrupamento, EDA e Dashboard Interativo

Disciplina: Análise e Visualização de Dados (AVD), CESAR School, 2026.2

## Integrantes

- Fernando Soares da Silva
- Luis Guilherme Lauria
- Adrian Michael de Araujo
- _(a preencher)_

## Datasets

| Parte | Dataset | Local no repositório |
|---|---|---|
| Parte Comum | Obesity, Estimation of Obesity Levels Based on Eating Habits and Physical Condition ([UCI 544](https://archive.ics.uci.edu/dataset/544)) | `data/parte_comum/obesity.csv` |
| Parte Específica | Credit Card Customers (BankChurners), [Kaggle](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers) | `data/parte_especifica/BankChurners.csv` |

O `BankChurners.csv` do repositório já está sem as duas últimas colunas do arquivo original do Kaggle
(`Naive_Bayes_Classifier_...`), que são saídas de um modelo e não dados dos clientes.

## Instalação

Requer Python 3.11 ou superior.

```bash
git clone https://github.com/Fernandosoares10/projeto_avd_.git
cd projeto_avd_

python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Execução

Todos os comandos abaixo partem da **raiz do projeto**, com o ambiente virtual ativado.

### Parte Comum (Obesity)

```bash
jupyter notebook notebooks/parte_comum/
```

Ordem sugerida dos notebooks:

| Ordem | Notebook | Conteúdo | Saídas em `out/parte_comum/` |
|---|---|---|---|
| 1 | `eda_comum.ipynb` | EDA estrutural, distribucional e outliers | gráficos `eda_*.png` e `obesity_tratado.csv` |
| 2 | `kmeans_passada2.ipynb` | Passada 2 (k fixo = 7): padronização, K-Means, visualização (PCA), mapeamento cluster → classe, matriz de confusão e métricas | `passada2_clusters_pca.png`, `passada2_matriz_confusao.png` |
| 3 | `kmeans_passada1.ipynb` | Passada 1 (k de 2 a 10): padronização, K-Means, Método do Cotovelo, visualização (PCA), mapeamento cluster → classe, matriz de confusão e métricas. A lógica está em `src/parte_comum/` e é testada em `tests/` | `passada1_cotovelo.png`, `passada1_clusters_pca.png`, `passada1_matriz_confusao.csv` |
| | _(a preencher: EDA relacional)_ | | |

### Parte Específica (BankChurners)

Notebooks em `src/parte_especifica/`. O `eda_unknown.ipynb` gera o dataset tratado usado pelos demais e pelo
dashboard, então deve ser executado antes deles.

| Ordem | Notebook | Conteúdo | Saídas em `out/parte_especifica/` |
|---|---|---|---|
| 1 | `eda_estrutural.ipynb` | Dimensões, tipos das variáveis e qualidade dos dados | |
| 2 | `eda_unknown.ipynb` | Valores Unknown: investigação do mecanismo de ausência e tratamento | `bankchurners_tratado.csv` |
| 3 | `eda_distribucional.ipynb` | Distribuição de cada variável | gráficos `eda_*.png` |
| 4 | `viz_exploratoria_1.ipynb` | Visualização exploratória 1 (boxplot de `Total_Trans_Amt` por situação do cliente) e nota analítica | `viz_exploratoria_1_boxplot_trans_amt.png` |
| 5 | `viz_exploratoria_2.ipynb` | Visualização exploratória 2 (violino de `Total_Trans_Ct` por situação do cliente) e nota analítica | `viz_exploratoria_2_violino_trans_ct.png` |
| 6 | `eda_outliers.ipynb` | Outliers (critérios IQR e z-score), plausibilidade, relação com o cancelamento e comparação das estratégias de tratamento. A lógica está em `outliers.py` e é testada em `tests/parte_especifica/` | `eda_outliers_boxplots.png`, `eda_outliers_cancelamento.png`, `eda_outliers_tratamento.png` |
| 7 | `viz_exploratoria_4.ipynb` | Visualização exploratória 4 (dispersão de `Total_Trans_Ct` × `Total_Trans_Amt`, colorida por situação do cliente) e nota analítica | `viz_exploratoria_4_dispersao_trans_ct_amt.png` |
| 8 | `viz_explanatoria_2.ipynb` | Visualização explanatória 2 (taxa de cancelamento por número de produtos, `Total_Relationship_Count`) e nota analítica | `viz_explanatoria_2_barras_produtos.png` |
| | _(a preencher: EDA relacional, visualização exploratória 3, explanatória 1)_ | | |

### Dashboard (Streamlit)

```bash
streamlit run src/parte_especifica/dashboard.py
```

O dashboard abre no navegador em `http://localhost:8501`. As páginas ficam em `src/parte_especifica/app_pages/` e
entram no menu lateral automaticamente quando o arquivo existe:

| Página | Arquivo |
|---|---|
| Início | `inicio.py` |
| Qualidade dos dados | `1_qualidade_dos_dados.py` |
| Distribuições | `2_distribuicoes.py` |
| Relações | `3_relacoes.py` |
| Outliers | `4_outliers.py` |
| Obesity: K-Means (Parte Comum) | `5_parte_comum.py` |

Funções e constantes compartilhadas pelas páginas (leitura dos dados, cores, dicionário das variáveis) ficam em
`src/parte_especifica/dados.py`.

## Testes

As funções da Passada 1 (`src/parte_comum/`) têm testes em `tests/`. As dependências de teste ficam num arquivo
separado para não alterar o `requirements.txt`:

```bash
pip install -r requirements-dev.txt
pytest --cov=src/parte_comum --cov-report=term-missing
```

## Estrutura de pastas

```
projeto-avd/
├─ README.md
├─ requirements.txt
├─ relatorio.pdf                      # relatório final (ambas as partes)
├─ docs/
│  ├─ DECLARACAO_IA.pdf               # declaração de uso de IA assinada por todos
│  └─ rascunhos/                      # rascunhos das seções do relatório
├─ data/
│  ├─ parte_comum/obesity.csv
│  └─ parte_especifica/BankChurners.csv
├─ out/
│  ├─ parte_comum/                    # gráficos e dataset tratado da Parte Comum
│  └─ parte_especifica/               # gráficos e dataset tratado da Parte Específica
├─ notebooks/
│  └─ parte_comum/                    # EDA e K-Means do Obesity
└─ src/
   ├─ parte_comum/
   └─ parte_especifica/
      ├─ *.ipynb                      # EDA e visualizações do BankChurners
      ├─ dashboard.py                 # ponto de entrada do Streamlit
      ├─ dados.py                     # leitura dos dados e constantes do dashboard
      └─ app_pages/                   # uma página do dashboard por arquivo
```

## Matriz de contribuição

Divisão das tarefas combinada pelo grupo. **R** = responsável pela entrega; **A** = apoio/revisão.

| Parte | Entregável | Fernando | Luis | Pedro | Adrian |
|---|---|:---:|:---:|:---:|:---:|
| Setup | Repositório, estrutura de pastas, `.gitignore`, `requirements.txt` | R | | | |
| Setup | Datasets em `data/` (BankChurners e Obesity) | R | R | | |
| Comum | EDA estrutural e distribucional (`eda_comum.ipynb`) | | R | | |
| Comum | EDA relacional (variáveis e classe) | | | R | |
| Comum | Outliers do Obesity | | R | | |
| Comum | K-Means Passada 1: k de 2 a 10, Cotovelo, mapeamento, matriz e métricas | | | | R |
| Comum | K-Means Passada 2: k fixo, mapeamento, matriz e métricas (`kmeans_passada2.ipynb`) | R | | | |
| Comum | Discussão sobre a granularidade das classes | | | R | |
| Específica | EDA estrutural (`eda_estrutural.ipynb`) | R | | | |
| Específica | Valores Unknown: mecanismo de ausência e tratamento (`eda_unknown.ipynb`) | R | | | |
| Específica | EDA distribucional (`eda_distribucional.ipynb`) | | R | | |
| Específica | EDA relacional e multivariada; variáveis derivadas | | | R | |
| Específica | Outliers do BankChurners | | | | R |
| Específica | Visualização exploratória 1 e nota analítica | R | | | |
| Específica | Visualização exploratória 2 e nota analítica (`viz_exploratoria_2.ipynb`) | | R | | |
| Específica | Visualização exploratória 3 e nota analítica | | | R | |
| Específica | Visualização exploratória 4 e nota analítica | | | | R |
| Específica | Visualização explanatória 1 (responde à pergunta de pesquisa) e nota | | | R | |
| Específica | Visualização explanatória 2 e nota | | | | R |
| Dashboard | Página inicial e navegação (`dashboard.py`, `dados.py`, `inicio.py`) | | R | | |
| Dashboard | Página Qualidade dos dados | R | | | |
| Dashboard | Página Distribuições, com filtros e exportação | | R | | |
| Dashboard | Página Relações, com comparação lado a lado e seleção de eixos | | | R | |
| Dashboard | Página Outliers | | | | R |
| Dashboard | Página da Parte Comum | | | | R |
| Entrega | Relatório: Passada 2 e EDA estrutural | R | | | |
| Entrega | Relatório: EDA da Parte Comum e distribuições | | R | | |
| Entrega | Relatório: relações e granularidade das classes | | | R | |
| Entrega | Relatório: Passada 1 e outliers | | | | R |
| Entrega | Montagem do `relatorio.pdf` e README final | R | A | A | A |
| Entrega | Revisão de ortografia e clareza do relatório | A | R | A | A |
| Entrega | Matriz de contribuição | | R | | |
| Entrega | Declaração de Uso de IA assinada por todos | A | A | R | A |
| Entrega | Teste final: clonar o repositório e rodar tudo | | | | R |
| Apresentação | Slides | A | A | R | A |

## Uso de IA

O grupo usou IA generativa conforme as regras do enunciado. Os trechos de código feitos com apoio de IA estão
marcados no próprio código com o comentário:

```python
# [IA] <ferramenta> – <finalidade>
```

A declaração completa, assinada por todos os integrantes, está em `docs/DECLARACAO_IA.pdf`.

_(a preencher pelo grupo: ferramentas usadas e para quê)_
