# [IA] Claude Code – funcoes e constantes compartilhadas pelas paginas do dashboard
"""Leitura dos dados e constantes usadas em todas as paginas do dashboard."""
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_BANK_TRATADO = RAIZ_PROJETO / "out" / "parte_especifica" / "bankchurners_tratado.csv"
CAMINHO_OBESITY = RAIZ_PROJETO / "data" / "parte_comum" / "obesity.csv"

COLUNA_ALVO = "Attrition_Flag"
CLIENTE_ATIVO = "Existing Customer"
CLIENTE_CANCELOU = "Attrited Customer"

# Ordem natural das categorias ordinais (usada em graficos e filtros)
ORDEM_CATEGORIAS = {
    "Education_Level": ["Uneducated", "High School", "College", "Graduate", "Post-Graduate", "Doctorate", "Unknown"],
    "Income_Category": ["Less than $40K", "$40K - $60K", "$60K - $80K", "$80K - $120K", "$120K +", "Unknown"],
    "Card_Category": ["Blue", "Silver", "Gold", "Platinum"],
}

# Significado de cada coluna do BankChurners (dicionario do Kaggle)
DICIONARIO_BANK = {
    "CLIENTNUM": ("Identificador do cliente", "identificador"),
    "Attrition_Flag": ("Situacao do cliente: ativo ou cancelou o cartao", "qualitativa nominal (alvo)"),
    "Customer_Age": ("Idade do cliente (anos)", "quantitativa discreta"),
    "Gender": ("Genero (F/M)", "qualitativa nominal"),
    "Dependent_count": ("Numero de dependentes", "quantitativa discreta"),
    "Education_Level": ("Escolaridade", "qualitativa ordinal"),
    "Marital_Status": ("Estado civil", "qualitativa nominal"),
    "Income_Category": ("Faixa de renda anual", "qualitativa ordinal"),
    "Card_Category": ("Categoria do cartao", "qualitativa ordinal"),
    "Months_on_book": ("Meses de relacionamento com o banco", "quantitativa discreta"),
    "Total_Relationship_Count": ("Quantidade de produtos do banco que o cliente tem", "quantitativa discreta"),
    "Months_Inactive_12_mon": ("Meses inativo nos ultimos 12 meses", "quantitativa discreta"),
    "Contacts_Count_12_mon": ("Contatos com o banco nos ultimos 12 meses", "quantitativa discreta"),
    "Credit_Limit": ("Limite de credito (US$)", "quantitativa continua"),
    "Total_Revolving_Bal": ("Saldo rotativo (US$)", "quantitativa continua"),
    "Avg_Open_To_Buy": ("Limite disponivel medio (US$)", "quantitativa continua"),
    "Total_Amt_Chng_Q4_Q1": ("Variacao do valor transacionado (4o tri / 1o tri)", "quantitativa continua"),
    "Total_Trans_Amt": ("Valor total transacionado em 12 meses (US$)", "quantitativa continua"),
    "Total_Trans_Ct": ("Quantidade de transacoes em 12 meses", "quantitativa discreta"),
    "Total_Ct_Chng_Q4_Q1": ("Variacao da quantidade de transacoes (4o tri / 1o tri)", "quantitativa continua"),
    "Avg_Utilization_Ratio": ("Taxa media de uso do limite (0 a 1)", "quantitativa continua"),
}


@st.cache_data
def carregar_bank() -> pd.DataFrame:
    """BankChurners apos o tratamento dos Unknown (gerado por eda_unknown.ipynb)."""
    return pd.read_csv(CAMINHO_BANK_TRATADO)


@st.cache_data
def carregar_obesity() -> pd.DataFrame:
    """Dataset Obesity original da Parte Comum."""
    return pd.read_csv(CAMINHO_OBESITY)
