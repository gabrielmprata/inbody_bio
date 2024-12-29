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


#######################
# Construção dos Gráficos

# 1. Avaliação
# Peso feito com st.metric direto no Main Panel


#######################
# Dashboard Main Panel

st.markdown("# :crossed_swords: Análise das medidas :hammer_and_pick:")

st.write(":blue[Avaliação:]", maxi, "	:date:")

with st.expander("Analise Músculo-Gordura", expanded=True):

    col = st.columns((1.1, 1.1, 1.1), gap='medium')

    with col[0]:
        #######################
        # Quadro com o total e a variação
        st.markdown('### Peso')
        st.metric(label="", value=str(
            (peso.Valor.values[0]).round(2)), delta=str(var_peso))

    with col[1]:
        st.markdown('### Massa Magra')

    with col[2]:
        st.markdown('### Massa de Gordura')

style_metric_cards(background_color="#071021",
                   border_left_color="#1f66bd", border_radius_px=5)
