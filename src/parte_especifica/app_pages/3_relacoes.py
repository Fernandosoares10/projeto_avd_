from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[3]
CAMINHO_TRATADO = RAIZ / "out" / "parte_especifica" / "bankchurners_tratado.csv"
CAMINHO_BRUTO = RAIZ / "data" / "parte_especifica" / "BankChurners.csv"

COR_ATIVO = "#4C72B0"
COR_CANCELADO = "#C44E52"


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    caminho = CAMINHO_TRATADO if CAMINHO_TRATADO.exists() else CAMINHO_BRUTO
    df = pd.read_csv(caminho)

    cols_descartar = [c for c in df.columns if c == "CLIENTNUM" or "Naive_Bayes" in c]
    if cols_descartar:
        df = df.drop(columns=cols_descartar)

    if pd.api.types.is_numeric_dtype(df["Attrition_Flag"]):
        df["cancelou"] = df["Attrition_Flag"].astype(int)
        df["Status"] = df["cancelou"].map({0: "Existing Customer", 1: "Attrited Customer"})
    else:
        df["cancelou"] = (df["Attrition_Flag"] == "Attrited Customer").astype(int)
        df["Status"] = df["Attrition_Flag"]

    return df


def main() -> None:
    st.markdown(
        "Exploração das correlações entre variáveis numéricas, interações comportamentais "
        "associadas ao cancelamento (`Attrition_Flag`) e verificação das variáveis derivadas no **BankChurners**."
    )

    df = carregar_dados()
    colunas_numericas = [
        c for c in df.select_dtypes(include="number").columns
        if c not in ["Attrition_Flag", "cancelou"]
    ]

    # Filtros laterais básicos (status e cartão)
    st.sidebar.header("Filtros — Relações")
    cartoes = sorted(df["Card_Category"].dropna().unique().tolist())
    cartoes_sel = st.sidebar.multiselect("Categoria do cartão", cartoes, default=cartoes)
    metodo_corr = st.sidebar.radio("Método de correlação", ["pearson", "spearman"], horizontal=True)

    df_filtrado = df[df["Card_Category"].isin(cartoes_sel)] if cartoes_sel else df.copy()
    if df_filtrado.empty:
        st.warning("Nenhum cliente corresponde aos filtros selecionados.")
        return

    taxa_geral = df_filtrado["cancelou"].mean() * 100
    corr_alvo = df_filtrado[colunas_numericas].corrwith(df_filtrado["cancelou"]).sort_values()
    var_mais_neg = corr_alvo.index[0]
    var_mais_pos = corr_alvo.index[-1]

    # KPIs principais
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Clientes filtrados", f"{len(df_filtrado):,}".replace(",", "."))
    k2.metric("Taxa de cancelamento", f"{taxa_geral:.2f}%")
    k3.metric("Maior associação negativa", var_mais_neg, f"r = {corr_alvo.iloc[0]:+.3f}", delta_color="off")
    k4.metric("Maior associação positiva", var_mais_pos, f"r = {corr_alvo.iloc[-1]:+.3f}", delta_color="off")

    st.divider()

    # 1. Matriz de correlação
    st.subheader(f"1. Matriz de correlação ({metodo_corr.capitalize()})")
    corr_mat = df_filtrado[colunas_numericas].corr(method=metodo_corr)
    fig_corr = px.imshow(
        corr_mat.round(2),
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    fig_corr.update_layout(height=600, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_corr, use_container_width=True)
    st.caption(
        "Destaque para a colinearidade quase perfeita entre `Credit_Limit` e `Avg_Open_To_Buy` "
        "e a forte relação entre `Total_Trans_Amt` e `Total_Trans_Ct`."
    )

    st.divider()

    # 2. Correlação com o cancelamento
    st.subheader("2. Associação das variáveis numéricas com o cancelamento")
    df_corr_alvo = pd.DataFrame({
        "Variável": corr_alvo.index,
        "Correlação": corr_alvo.values,
        "Direção": np.where(corr_alvo.values >= 0, "Maior nos cancelados", "Menor nos cancelados"),
    })
    fig_bar = px.bar(
        df_corr_alvo,
        x="Correlação",
        y="Variável",
        orientation="h",
        color="Direção",
        color_discrete_map={
            "Maior nos cancelados": COR_CANCELADO,
            "Menor nos cancelados": COR_ATIVO,
        },
        text=df_corr_alvo["Correlação"].map(lambda v: f"{v:+.3f}"),
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(height=480, yaxis_title="", xaxis_title="Correlação de Pearson com cancelou")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 3. Heatmap Contatos x Meses Inativos (Visualização Exploratória 3)
    st.subheader("3. Interação de risco: Contatos × Meses Inativos (12 meses)")
    taxa_piv = (
        df_filtrado.pivot_table(
            index="Contacts_Count_12_mon",
            columns="Months_Inactive_12_mon",
            values="cancelou",
            aggfunc="mean",
        )
        * 100
    )
    contagem_piv = df_filtrado.pivot_table(
        index="Contacts_Count_12_mon",
        columns="Months_Inactive_12_mon",
        values="cancelou",
        aggfunc="count",
        fill_value=0,
    )

    texto_celulas = [
        [
            f"{taxa_piv.loc[i, j]:.1f}%<br>(n={int(contagem_piv.loc[i, j])})"
            if int(contagem_piv.loc[i, j]) > 0 and pd.notna(taxa_piv.loc[i, j])
            else "-"
            for j in taxa_piv.columns
        ]
        for i in taxa_piv.index
    ]

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=taxa_piv.values,
            x=[str(c) for c in taxa_piv.columns],
            y=[str(i) for i in taxa_piv.index],
            text=texto_celulas,
            texttemplate="%{text}",
            colorscale="YlOrRd",
            zmin=0,
            zmax=100,
            colorbar={"title": "Cancelamento (%)"},
        )
    )
    fig_heat.update_layout(
        height=480,
        xaxis_title="Meses de inatividade (Months_Inactive_12_mon)",
        yaxis_title="Contatos com o banco (Contacts_Count_12_mon)",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    # 4. Visualização Explanatória 1: Volume de transações x queda no Q4
    st.subheader("4. Volume de transações × Queda no 4º trimestre (Q4/Q1)")
    bins_trans = [0, 39, 59, 79, np.inf]
    rotulos_trans = ["< 40 transações", "40 a 59 transações", "60 a 79 transações", "80+ transações"]
    df_exp = df_filtrado.assign(
        faixa_trans=pd.cut(df_filtrado["Total_Trans_Ct"], bins=bins_trans, labels=rotulos_trans, right=True),
        ritmo_q4=np.where(
            df_filtrado["Total_Ct_Chng_Q4_Q1"] < 0.60,
            "Queda forte no Q4 (Q4/Q1 < 0,60)",
            "Uso estável/crescente (Q4/Q1 ≥ 0,60)",
        ),
    )
    resumo_exp = (
        df_exp.groupby(["faixa_trans", "ritmo_q4"], observed=True)["cancelou"]
        .agg(taxa=lambda s: s.mean() * 100, total="count")
        .reset_index()
    )
    resumo_exp["rotulo"] = resumo_exp.apply(lambda r: f"{r['taxa']:.1f}% (n={int(r['total'])})", axis=1)

    fig_exp = px.bar(
        resumo_exp,
        x="faixa_trans",
        y="taxa",
        color="ritmo_q4",
        barmode="group",
        text="rotulo",
        color_discrete_map={
            "Queda forte no Q4 (Q4/Q1 < 0,60)": COR_CANCELADO,
            "Uso estável/crescente (Q4/Q1 ≥ 0,60)": COR_ATIVO,
        },
        labels={"faixa_trans": "Faixa de transações anuais", "taxa": "Taxa de cancelamento (%)", "ritmo_q4": "Ritmo Q4/Q1"},
    )
    fig_exp.add_hline(
        y=taxa_geral,
        line_dash="dash",
        line_color="#333333",
        annotation_text=f"Média filtrada: {taxa_geral:.1f}%",
        annotation_position="top right",
    )
    fig_exp.update_traces(textposition="outside")
    fig_exp.update_layout(height=480, yaxis_range=[0, min(resumo_exp["taxa"].max() + 18, 108)])
    st.plotly_chart(fig_exp, use_container_width=True)

    st.divider()

    # 5. Variáveis derivadas
    st.subheader("5. Variáveis derivadas documentadas")
    c1, c2 = st.columns(2)
    erro_open = (df_filtrado["Avg_Open_To_Buy"] - (df_filtrado["Credit_Limit"] - df_filtrado["Total_Revolving_Bal"])).abs().max()
    erro_util = (df_filtrado["Avg_Utilization_Ratio"] - (df_filtrado["Total_Revolving_Bal"] / df_filtrado["Credit_Limit"])).abs().max()

    with c1:
        st.info(
            f"**`Avg_Open_To_Buy`** = `Credit_Limit - Total_Revolving_Bal`  \n"
            f"Erro máximo absoluto: **{erro_open:.4f}** | Correlação com `Credit_Limit`: "
            f"**{df_filtrado['Avg_Open_To_Buy'].corr(df_filtrado['Credit_Limit']):.4f}**.  \n"
            "Redundante em modelos lineares; descartar junto a `Credit_Limit` e `Total_Revolving_Bal`."
        )
    with c2:
        st.info(
            f"**`Avg_Utilization_Ratio`** = `Total_Revolving_Bal / Credit_Limit`  \n"
            f"Erro máximo absoluto: **{erro_util:.4f}** | Correlação com cancelamento: "
            f"**{df_filtrado['Avg_Utilization_Ratio'].corr(df_filtrado['cancelou']):+.4f}**.  \n"
            "Informativa para visualização e diagnóstico de desengajamento."
        )


main()
