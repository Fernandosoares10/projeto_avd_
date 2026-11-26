# [IA] Claude Code – pagina Relacoes do dashboard (filtros, correlacoes, heatmap, explanatorias 1 e 2, comparacao lado a lado e explorador X x Y)
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from explanatoria_produtos import secao_produtos

RAIZ = Path(__file__).resolve().parents[3]
CAMINHO_TRATADO = RAIZ / "out" / "parte_especifica" / "bankchurners_tratado.csv"
CAMINHO_BRUTO = RAIZ / "data" / "parte_especifica" / "BankChurners.csv"

COR_ATIVO = "#4C72B0"
COR_CANCELADO = "#C44E52"
COR_PERFIL_A = "#4C72B0"
COR_PERFIL_B = "#DD8452"


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


def renderizar_cartao_perfil(df_perfil: pd.DataFrame, titulo: str, taxa_ref: float) -> None:
    st.markdown(f"#### {titulo}")
    n_cli = len(df_perfil)
    taxa_churn = df_perfil["cancelou"].mean() * 100 if n_cli > 0 else 0.0
    delta_taxa = taxa_churn - taxa_ref

    m1, m2 = st.columns(2)
    m1.metric("Clientes", f"{n_cli:,}".replace(",", "."))
    m2.metric(
        "Taxa de cancelamento",
        f"{taxa_churn:.2f}%",
        f"{delta_taxa:+.2f} p.p. vs. base filtrada",
        delta_color="inverse",
    )

    m3, m4 = st.columns(2)
    m3.metric("Mediana de transações", f"{df_perfil['Total_Trans_Ct'].median():.0f}")
    m4.metric("Mediana valor transac.", f"$ {df_perfil['Total_Trans_Amt'].median():,.0f}".replace(",", "."))

    m5, m6 = st.columns(2)
    m5.metric("Mediana saldo rotativo", f"$ {df_perfil['Total_Revolving_Bal'].median():,.0f}".replace(",", "."))
    m6.metric("Média de contatos (12m)", f"{df_perfil['Contacts_Count_12_mon'].mean():.2f}")


def main() -> None:
    st.markdown(
        "Exploração das correlações entre variáveis numéricas, interações comportamentais "
        "associadas ao cancelamento (`Attrition_Flag`), verificação das variáveis derivadas, "
        "**comparação lado a lado** entre perfis e **explorador interativo X × Y** no **BankChurners**."
    )

    df = carregar_dados()
    colunas_numericas = [
        c for c in df.select_dtypes(include="number").columns
        if c not in ["Attrition_Flag", "cancelou"]
    ]

    # Filtros laterais básicos (cartão e método de correlação)
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
    st.plotly_chart(fig_corr, width="stretch")
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
    st.plotly_chart(fig_bar, width="stretch")

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
    st.plotly_chart(fig_heat, width="stretch")

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
    st.plotly_chart(fig_exp, width="stretch")

    st.divider()

    # [IA] Claude Code – explanatoria 2 movida da pagina Outliers para ficar junto da explanatoria 1
    secao_produtos()

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

    st.divider()

    # 6. Bônus 1 — Comparação lado a lado entre perfis
    st.subheader("6. Comparação lado a lado entre perfis de clientes")
    st.caption(
        "Escolha uma dimensão de segmentação e selecione dois grupos (Perfil A e Perfil B) "
        "para comparar métricas comportamentais, distribuição e dispersão lado a lado."
    )

    dimensoes_disponiveis = {
        "Status (Ativo vs. Cancelado)": "Status",
        "Categoria do cartão": "Card_Category",
        "Faixa de renda": "Income_Category",
        "Escolaridade": "Education_Level",
        "Estado civil": "Marital_Status",
        "Gênero": "Gender",
    }
    dimensoes_validas = {
        rotulo: col for rotulo, col in dimensoes_disponiveis.items()
        if col in df_filtrado.columns and df_filtrado[col].nunique() >= 2
    }

    tabela_comp = None
    if not dimensoes_validas:
        st.info("Selecione mais categorias nos filtros laterais para habilitar a comparação lado a lado.")
    else:
        s1, s2, s3 = st.columns([1.2, 1, 1])
        with s1:
            rotulo_dim = st.selectbox("Dimensão de comparação", list(dimensoes_validas.keys()))
            col_dim = dimensoes_validas[rotulo_dim]
            opcoes_grupo = sorted(df_filtrado[col_dim].dropna().unique().tolist())

        idx_a = opcoes_grupo.index("Existing Customer") if "Existing Customer" in opcoes_grupo else 0
        idx_b = opcoes_grupo.index("Attrited Customer") if "Attrited Customer" in opcoes_grupo else min(1, len(opcoes_grupo) - 1)

        with s2:
            perfil_a = st.selectbox("Perfil A (esquerda)", opcoes_grupo, index=idx_a, key="comp_perfil_a")
        with s3:
            perfil_b = st.selectbox("Perfil B (direita)", opcoes_grupo, index=idx_b, key="comp_perfil_b")

        df_a = df_filtrado[df_filtrado[col_dim] == perfil_a]
        df_b = df_filtrado[df_filtrado[col_dim] == perfil_b]

        col_esq, col_dir = st.columns(2)
        with col_esq:
            renderizar_cartao_perfil(df_a, f"Perfil A: {perfil_a}", taxa_geral)
        with col_dir:
            renderizar_cartao_perfil(df_b, f"Perfil B: {perfil_b}", taxa_geral)

        # Gráficos comparativos lado a lado
        var_comp = st.selectbox(
            "Variável numérica para comparar distribuições",
            colunas_numericas,
            index=colunas_numericas.index("Total_Trans_Ct") if "Total_Trans_Ct" in colunas_numericas else 0,
        )

        df_comp = pd.concat([
            df_a.assign(Grupo=f"A: {perfil_a}"),
            df_b.assign(Grupo=f"B: {perfil_b}"),
        ], ignore_index=True)

        mapa_cores = {
            f"A: {perfil_a}": COR_PERFIL_A,
            f"B: {perfil_b}": COR_PERFIL_B if perfil_b != perfil_a else COR_PERFIL_A,
        }

        g1, g2 = st.columns(2)
        with g1:
            fig_box_comp = px.box(
                df_comp,
                x="Grupo",
                y=var_comp,
                color="Grupo",
                color_discrete_map=mapa_cores,
                title=f"Distribuição (Boxplot): {var_comp}",
            )
            fig_box_comp.update_layout(showlegend=False, height=400, xaxis_title="")
            st.plotly_chart(fig_box_comp, width="stretch")

        with g2:
            fig_hist_comp = px.histogram(
                df_comp,
                x=var_comp,
                color="Grupo",
                barmode="overlay",
                histnorm="percent",
                opacity=0.6,
                color_discrete_map=mapa_cores,
                title=f"Densidade relativa (%): {var_comp}",
                labels={"count": "% do grupo"},
            )
            fig_hist_comp.update_layout(height=400, yaxis_title="% de clientes no perfil")
            st.plotly_chart(fig_hist_comp, width="stretch")

        # Tabela resumo lado a lado das principais métricas comportamentais
        metricas_tabela = [
            "Total_Trans_Ct",
            "Total_Trans_Amt",
            "Total_Ct_Chng_Q4_Q1",
            "Total_Revolving_Bal",
            "Avg_Utilization_Ratio",
            "Contacts_Count_12_mon",
            "Months_Inactive_12_mon",
            "Credit_Limit",
        ]
        metricas_tabela = [m for m in metricas_tabela if m in df_filtrado.columns]

        tabela_comp = pd.DataFrame({
            f"Média — {perfil_a}": df_a[metricas_tabela].mean(),
            f"Mediana — {perfil_a}": df_a[metricas_tabela].median(),
            f"Média — {perfil_b}": df_b[metricas_tabela].mean(),
            f"Mediana — {perfil_b}": df_b[metricas_tabela].median(),
        })
        tabela_comp["Diferença (Média B - A)"] = (
            tabela_comp[f"Média — {perfil_b}"] - tabela_comp[f"Média — {perfil_a}"]
        )
        st.dataframe(tabela_comp.round(2), width="stretch")

    st.divider()

    # 7. Bônus 2 — Explorador interativo de dispersão (X x Y) e exportação CSV
    st.subheader("7. Explorador interativo de dispersão (X × Y) e exportação")
    st.caption(
        "Combine livremente duas variáveis numéricas para inspecionar relações lineares/não-lineares, "
        "segmentar por cor e exportar os dados filtrados."
    )

    e1, e2, e3 = st.columns(3)
    idx_x = colunas_numericas.index("Total_Trans_Ct") if "Total_Trans_Ct" in colunas_numericas else 0
    idx_y = colunas_numericas.index("Total_Trans_Amt") if "Total_Trans_Amt" in colunas_numericas else min(1, len(colunas_numericas) - 1)

    with e1:
        var_x = st.selectbox("Variável do eixo X", colunas_numericas, index=idx_x, key="exp_var_x")
    with e2:
        var_y = st.selectbox("Variável do eixo Y", colunas_numericas, index=idx_y, key="exp_var_y")

    opcoes_cor = [
        c for c in ["Status", "Card_Category", "Income_Category", "Gender", "Education_Level", "Marital_Status"]
        if c in df_filtrado.columns
    ]
    with e3:
        var_cor = st.selectbox("Colorir pontos por", opcoes_cor, index=0, key="exp_var_cor")

    c_opt1, c_opt2 = st.columns([1, 2])
    with c_opt1:
        mostrar_tendencia = st.checkbox("Exibir reta de tendência linear", value=True)
    with c_opt2:
        apenas_cancelados = st.checkbox("Destacar apenas clientes que cancelaram (Attrited Customer)", value=False)

    df_scatter = df_filtrado[df_filtrado["cancelou"] == 1] if apenas_cancelados else df_filtrado
    df_xy = df_scatter[[var_x, var_y, var_cor]].dropna()

    r_pearson = df_xy[var_x].corr(df_xy[var_y], method="pearson") if len(df_xy) > 1 else np.nan
    r_spearman = df_xy[var_x].corr(df_xy[var_y], method="spearman") if len(df_xy) > 1 else np.nan

    p1, p2, p3 = st.columns(3)
    p1.metric("Pontos exibidos", f"{len(df_xy):,}".replace(",", "."))
    p2.metric("Correlação de Pearson (r)", f"{r_pearson:+.3f}" if pd.notna(r_pearson) else "N/A")
    p3.metric("Correlação de Spearman (ρ)", f"{r_spearman:+.3f}" if pd.notna(r_spearman) else "N/A")

    mapa_cor_scatter = (
        {"Existing Customer": COR_ATIVO, "Attrited Customer": COR_CANCELADO}
        if var_cor == "Status"
        else None
    )
    hover_cols = [
        c for c in ["Status", "Card_Category", "Total_Trans_Ct", "Total_Trans_Amt", "Contacts_Count_12_mon", "Months_Inactive_12_mon"]
        if c in df_scatter.columns and c not in [var_x, var_y, var_cor]
    ]

    fig_scatter = px.scatter(
        df_scatter,
        x=var_x,
        y=var_y,
        color=var_cor,
        color_discrete_map=mapa_cor_scatter,
        opacity=0.55,
        hover_data=hover_cols,
        title=f"Dispersão: {var_x} × {var_y} (colorido por {var_cor})",
    )

    if mostrar_tendencia and len(df_xy) > 1 and df_xy[var_x].nunique() > 1:
        coef_ang, coef_lin = np.polyfit(df_xy[var_x], df_xy[var_y], 1)
        x_linha = np.linspace(df_xy[var_x].min(), df_xy[var_x].max(), 100)
        y_linha = coef_ang * x_linha + coef_lin
        fig_scatter.add_trace(
            go.Scatter(
                x=x_linha,
                y=y_linha,
                mode="lines",
                name="Tendência linear",
                line={"color": "#FFFFFF", "width": 2, "dash": "dash"},
            )
        )

    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, width="stretch")

    # Exportação de dados em CSV
    st.markdown("#### Exportação de dados")
    d1, d2 = st.columns(2)
    with d1:
        csv_filtrado = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar base filtrada (CSV)",
            data=csv_filtrado,
            file_name="bankchurners_relacoes_filtrado.csv",
            mime="text/csv",
            width="stretch",
        )
    with d2:
        if tabela_comp is not None:
            csv_comp = tabela_comp.round(4).to_csv().encode("utf-8")
            st.download_button(
                label="Baixar tabela de comparação de perfis (CSV)",
                data=csv_comp,
                file_name="bankchurners_comparacao_perfis.csv",
                mime="text/csv",
                width="stretch",
            )


main()