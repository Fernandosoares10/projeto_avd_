# Projeto Final AVD: Agrupamento, EDA e Dashboard Interativo

Disciplina: Análise e Visualização de Dados (AVD), CESAR School, 2026.2

## Integrantes

- Fernando Soares da Silva
- Luis Guilherme Lauria
- _(a preencher)_
- _(a preencher)_

## Datasets

| Parte | Dataset | Local no repositório |
|---|---|---|
| Parte Comum | Obesity, Estimation of Obesity Levels Based on Eating Habits and Physical Condition ([UCI 544](https://archive.ics.uci.edu/dataset/544)) | `data/parte_comum/obesity.csv` |
| Parte Específica | Credit Card Customers (BankChurners), [Kaggle](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers) | `data/parte_especifica/BankChurners.csv` |

## Instalação

Requer Python 3.11 ou superior.

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Execução

Parte Comum (notebooks):

```bash
jupyter notebook notebooks/parte_comum/
```

Parte Específica (dashboard):

```bash
streamlit run src/parte_especifica/dashboard.py
```

## Estrutura de pastas

```
projeto-avd/
├─ README.md
├─ requirements.txt
├─ docs/                  # DECLARACAO_IA.pdf
├─ data/
│  ├─ parte_comum/
│  └─ parte_especifica/
├─ out/
│  ├─ parte_comum/
│  └─ parte_especifica/
├─ notebooks/
│  └─ parte_comum/
├─ src/
│  ├─ parte_comum/
│  └─ parte_especifica/
└─ relatorio.pdf
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

_(a preencher; declaração assinada em `docs/DECLARACAO_IA.pdf`)_
