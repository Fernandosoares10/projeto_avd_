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

_(a preencher)_

## Uso de IA

_(a preencher; declaração assinada em `docs/DECLARACAO_IA.pdf`)_
