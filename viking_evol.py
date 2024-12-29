#######################
# Importando libraries
import streamlit as st
import altair as alt
import json
from urllib.request import urlopen
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards


#######################
# Configuração da página
st.set_page_config(
    page_title="Evolua como um Viking",
    page_icon=":muscle:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

alt.themes.enable("dark")

#######################
# Projeto utilizando streamlit_extras.metric_cards
# pip install streamlit-extras
# streamlit-extras==0.3.5
# https://arnaudmiribel.github.io/streamlit-extras/extras/metric_cards/


#######################
# Carregando dataset


@st.cache_data
def load_data():
    return pd.read_excel("https://raw.githubusercontent.com/gabrielmprata/inbody_bio/main/dataset/evol_python.xlsx", sheet_name='inbody_full')


df_inbody_full = load_data()

df_inbody_full['data'] = pd.to_datetime(df_inbody_full['data'])
df_inbody_full['ano_mes'] = df_inbody_full['data'].dt.strftime('%Y-%m')

# Param
maxi = '2024-12'
mes_ant = '2024-11'

# Construção dos Datasets
# 1. Avaliação
# Peso

peso = (df_inbody_full[['Valor']]
        [(df_inbody_full['ano_mes'] == maxi) & (df_inbody_full['kpi'] == 5)]
        )

peso_ant = (df_inbody_full[['Valor']]
            [(df_inbody_full['ano_mes'] == mes_ant) & (df_inbody_full['kpi'] == 5)]
            )

var_peso = (peso.Valor.values[0] - peso_ant.Valor.values[0]).round(2)

# Massa de gordura
gordura = (df_inbody_full[['Valor']]
           [(df_inbody_full['ano_mes'] == maxi) & (df_inbody_full['kpi'] == 4)]
           )

gordura_ant = (df_inbody_full[['Valor']]
               [(df_inbody_full['ano_mes'] == mes_ant)
                & (df_inbody_full['kpi'] == 4)]
               )

var_gordura = (gordura.Valor.values[0] - gordura_ant.Valor.values[0]).round(2)

# Massa Muscular Esquelética
massa = (df_inbody_full[['Valor']]
         [(df_inbody_full['ano_mes'] == maxi) & (df_inbody_full['kpi'] == 6)]
         )

massa_ant = (df_inbody_full[['Valor']]
             [(df_inbody_full['ano_mes'] == mes_ant)
              & (df_inbody_full['kpi'] == 6)]
             )

var_massa = (massa.Valor.values[0] - massa_ant.Valor.values[0]).round(2)

# Porcentual de gordura
pgc = (df_inbody_full[['Valor']]
       [(df_inbody_full['ano_mes'] == maxi) & (df_inbody_full['kpi'] == 8)]
       )

pgc_ant = (df_inbody_full[['Valor']]
           [(df_inbody_full['ano_mes'] == mes_ant) & (df_inbody_full['kpi'] == 8)]
           )

var_pgc = (pgc.Valor.values[0] - pgc_ant.Valor.values[0]).round(2)

# ----------------------------------------------------------------------------#
# 2. Análise músculo gordura
df_inbody_full_gr = (df_inbody_full[['ano_mes', 'Metrica', 'kpi', 'Valor']]).query(
    'kpi in (4, 5, 6) ')

# ----------------------------------------------------------------------------#
# 3. Porcentual de gordura
df_inbody_pgc = (
    df_inbody_full[['ano_mes', 'Metrica', 'kpi', 'Valor']]).query('kpi == 8')


#######################
# Construção dos Gráficos

# 1. Avaliação
# todos os cards foram feitos com st.metric direto no Main Panel

# ----------------------------------------------------------------------------#
# 2. Análise músculo gordura
hist = px.line(df_inbody_full_gr, x='ano_mes', y='Valor', color='Metrica',
               markers=True, text='Valor',
               # height=600, width=800, #altura x largura
               line_shape="spline",
               template="plotly_dark",
               render_mode="svg",
               color_discrete_sequence=["blue", "green", "red"],
               category_orders={"Metrica": [
                   "Peso", "Massa Muscular Esquelética", "Massa de gordura"]},
               labels=dict(ano_mes="Ano e mês",
                           Valor="Kg", variable="Métrica")
               )

hist.update_layout(legend=dict(
    yanchor="top",
    y=-0.3,
    xanchor="left",
    x=0.01))
# se o type for date, vai respeitar o intervalo
hist.update_xaxes(type="category")
hist.update_traces(line_width=2, textposition='top center')

# -------------------------------------------------------#
# 3 Porcentual de Gordura
gr_pcg = px.line(df_inbody_pgc, x='ano_mes', y='Valor', color='Metrica',
                 markers=True, text='Valor',
                 height=150, width=800,  # altura x largura
                 line_shape="spline",
                 template="plotly_dark",
                 render_mode="svg",
                 color_discrete_sequence=["orange"],

                 labels=dict(ano_mes="Ano e mês",
                             Valor="%", variable="Métrica")
                 )
# se o type for date, vai respeitar o intervalo
gr_pcg.update_xaxes(type="category")
gr_pcg.update_layout(margin=dict(t=1, b=0, l=0, r=0), showlegend=False)
gr_pcg.update_traces(line_width=2, textposition='top center')


#######################
# Dashboard Main Panel

st.image("https://raw.githubusercontent.com/gabrielmprata/inbody_bio/main/img/Header_Viking3.jpg")
st.markdown("# :crossed_swords: Viking Evolution :hammer_and_pick:")

st.write(":blue[Avaliação:]", maxi, "	:date:")

style_metric_cards(background_color="#071021",
                   border_left_color="#1f66bd", border_radius_px=5)

with st.expander("Analise Músculo-Gordura", expanded=True):

    col = st.columns((1.1, 1.1, 1.1, 1.1), gap='medium')

    with col[0]:
        #######################
        # Quadro com o total e a variação
        st.markdown('### Peso')
        st.metric(label="", value=str(
            (peso.Valor.values[0]).round(2)), delta=str(var_peso))

    with col[1]:
        st.markdown('### Massa Magra')
        st.metric(label="", value=str(
            (massa.Valor.values[0]).round(2)), delta=str(var_massa))

    with col[2]:
        st.markdown('### Massa Gorda')
        st.metric(delta_color="inverse", label="", value=str(
            (gordura.Valor.values[0]).round(2)), delta=str(var_gordura))

    with col[3]:
        st.markdown('### % Gordura')
        st.metric(delta_color="inverse", label="", value=str(
            (pgc.Valor.values[0]).round(2)), delta=str(var_pgc))

with st.expander("Histórico", expanded=True):
    st.plotly_chart(hist, use_container_width=True)

with st.expander("Histórico do Porcentual de Gordura", expanded=True):
    st.plotly_chart(gr_pcg, use_container_width=True)
