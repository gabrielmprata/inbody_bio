#######################
# Importando libraries
import streamlit as st
import altair as alt
import json
from urllib.request import urlopen
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import plotly.express as px


#######################
# Configuração da página
st.set_page_config(
    page_title="Perfil",
    page_icon="☎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

alt.themes.enable("dark")

########################
# Style
st.markdown("""
<style>

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
     
}

[data-testid="metric-container"] {
   color: rgb(5, 4, 4);
}         

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}            

</style>
""", unsafe_allow_html=True)


#######################
# Carregando dataset


@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/gabrielmprata/inbody_bio/main/dataset/perfil.csv.bz2", sep=',')


df_perfil = load_data()

df_regiao = pd.read_csv(
    "https://raw.githubusercontent.com/gabrielmprata/Anatel_Reclamacoes/main/datasets/regiao_br.csv", encoding="utf-8", sep=';')

df_uf_hist = pd.read_csv(
    "https://raw.githubusercontent.com/gabrielmprata/inbody_bio/main/dataset/uf_hist.csv", encoding="utf-8", sep=';')

# carrega dataset com o caminho das imagens
UF_flag = pd.read_csv(
    'https://raw.githubusercontent.com/gabrielmprata/anatel/refs/heads/main/datasets/UF_flags.csv', encoding="utf_8", sep=';')


# Construção dos Datasets
# 5.1 Visao geral da planta

# maxi = df_perfil.ano_mes.max()  # último mês
# mes_ant = df_perfil.dt_mes.max()
# mes_ant = mes_ant - DateOffset(months=1)  # mês anterior

maxi = '2024-09'
mes_ant = '2024-08'

# resumo último mês
df_res_plt = (df_perfil[['dt_base', 'qtd_voip']]
              [(df_perfil['ano_mes'] == maxi)]
              ).groupby(['dt_base'])['qtd_voip'].sum().reset_index()

df_res_plt['acessos'] = (df_res_plt['qtd_voip']/1000000).round(2)


# resumo mês anterior
df_res_ant = (df_perfil[['dt_base', 'qtd_voip']]
              [(df_perfil['ano_mes'] == mes_ant)]
              ).groupby(['dt_base'])['qtd_voip'].sum().reset_index()

var_ano = (df_res_plt.qtd_voip.values[0] -
           df_res_ant.qtd_voip.values[0]).round(2)

#######################
# 5.2 Gain/Loss UF
# resumo mês atual
df_uf_atu = (df_perfil[['dt_mes', 'nome_estado', 'qtd_voip']]
             [(df_perfil['ano_mes'] == maxi)]
             ).groupby(['nome_estado'])['qtd_voip'].sum().reset_index()

# resumo mês anterior
df_uf_ant = (df_perfil[['dt_mes', 'nome_estado', 'qtd_voip']]
             [(df_perfil['ano_mes'] == mes_ant)]
             ).groupby(['nome_estado'])['qtd_voip'].sum().reset_index()

# Merge por UF
df_uf_gl = pd.merge(df_uf_atu, df_uf_ant, left_on=[
                    'nome_estado'], right_on=['nome_estado'], how='left')

# diferença entre os meses
df_uf_gl['dif'] = df_uf_gl['qtd_voip_x'] - df_uf_gl['qtd_voip_y']

# Estado com mais ganho e mais perda de clientes
ind_gain = df_uf_gl.sort_values(by='dif', ascending=False).head(1)
ind_loss = df_uf_gl.sort_values(by='dif', ascending=True).head(1)

#######################
# 5.3 Mapa
# resumo por UF do mês atual
df_uf = (df_perfil[['dt_mes', 'uf', 'qtd_voip']]
         [(df_perfil['ano_mes'] == maxi)]
         ).groupby(['uf'])['qtd_voip'].sum().reset_index()

#######################
# 5.4 Historico UF/TOP
df_uf_hist.sort_values(by='20240930', ascending=False, inplace=True)

df_uf_hist = pd.merge(df_uf_hist, UF_flag,  left_on='uf', right_on='uf')


#######################
# 5.4 Por unidade de negocio
# Dataframe agrupando por grupo unidade
df_un = (df_perfil[['grupo_unidade', 'qtd_voip']]
         [(df_perfil['ano_mes'] == maxi)]
         ).groupby(['grupo_unidade'])['qtd_voip'].sum().reset_index()

#######################
# 5.5 Por idade
# Dataframe agrupando por idade
df_idade = (df_perfil[['idade', 'qtd_voip']]
            [(df_perfil['ano_mes'] == maxi) & (df_perfil['idade'] != 'NI')]
            ).groupby(['idade'])['qtd_voip'].sum().reset_index()

#######################
# 5.6 Representatividade por regiao
# Dataframe agrupando por região
df_uf_reg = (df_perfil[['regiao', 'uf', 'qtd_voip']]
             [(df_perfil['ano_mes'] == maxi)]
             ).groupby(['regiao', 'uf'])['qtd_voip'].sum().reset_index()

#######################
# 5.7 Trafego
# Dataframe agrupando por perfil de trafego
df_voz = (df_perfil[['perfil_voip', 'qtd_voip']]
          [(df_perfil['ano_mes'] == maxi)]
          ).groupby(['perfil_voip'])['qtd_voip'].sum().reset_index()

df_voz['perfil'] = df_voz.perfil_voip.apply(
    lambda x: 'SEM TRAFEGO' if x == 'SEM CDR' else 'COM TRAFEGO'
)

#######################
# 5.8 Acessos por tipo de Trafego
# tabela historica
df_voip_traf = df_perfil[['dt_mes', 'ano_mes', 'qtd_voip_local_ff',
                          'qtd_voip_local_fm', 'qtd_voip_ldn_ff', 'qtd_voip_ldn_fm']]
df_voip_traf = df_voip_traf.groupby(["dt_mes", 'ano_mes']).sum(
    ['qtd_voip_local_ff', 'qtd_voip_local_fm', 'qtd_voip_ldn_ff', 'qtd_voip_ldn_fm']).reset_index()

df_voip_traf_max = (df_voip_traf[['dt_mes', 'qtd_voip_local_ff', 'qtd_voip_local_fm', 'qtd_voip_ldn_ff', 'qtd_voip_ldn_fm']]
                    [(df_voip_traf['ano_mes'] == maxi)]
                    )
# renomeando as colunas
df_voip_traf_max.rename(columns={'qtd_voip_local_ff': 'Local_FF',
                                 'qtd_voip_local_fm': 'Local_FM',
                                 'qtd_voip_ldn_ff': 'LDN_FF',
                                 'qtd_voip_ldn_fm': 'LDN_FM'
                                 }, inplace=True)
# Transformando colunas em linhas
df_voip_traf_max = pd.melt(df_voip_traf_max, id_vars=['dt_mes'])


#######################
# 5.9 Minutos por tipo de Trafego
# tabela historica
df_traf_min = df_perfil[['dt_mes', 'ano_mes', 'qt_min_local_ff', 'qt_min_local_fm',
                         'qt_min_ldn_ff', 'qt_min_ldn_fm', 'qt_min_ngeo', 'qt_min_ldi', 'total_minutos_sainte']]
df_traf_min = df_traf_min.groupby(["dt_mes", 'ano_mes']).sum(['qt_min_local_ff', 'qt_min_local_fm',
                                                              'qt_min_ldn_ff', 'qt_min_ldn_fm', 'qt_min_ngeo', 'qt_min_ldi', 'total_minutos_sainte']).reset_index()

df_traf_min_max = (df_traf_min[['dt_mes', 'qt_min_local_ff', 'qt_min_local_fm', 'qt_min_ldn_ff', 'qt_min_ldn_fm', 'qt_min_ngeo', 'qt_min_ldi']]
                   [(df_traf_min['ano_mes'] == maxi)]
                   )
# renomeando as colunas
df_traf_min_max.rename(columns={'qt_min_local_ff': 'Local_FF',
                                'qt_min_local_fm': 'Local_FM',
                                'qt_min_ldn_ff': 'LDN_FF',
                                'qt_min_ldn_fm': 'LDN_FM',
                                'qt_min_ngeo': 'NGEO',
                                'qt_min_ldi': 'LDI'
                                }, inplace=True)
# Transformando colunas em linhas
df_traf_min_max = pd.melt(df_traf_min_max, id_vars=['dt_mes'])

#######################
# 6.1 Historico planta
# Historico 2000 a 2023
df_hist = df_perfil.groupby(["dt_base"])['qtd_voip'].sum().reset_index()

# Variação
df_hist['qtd_ant'] = df_hist.qtd_voip.shift(1)
df_hist['var'] = (((df_hist['qtd_voip']/df_hist['qtd_ant'])*100)-100).round(2)
df_hist['dif'] = (df_hist['qtd_voip']-df_hist['qtd_ant'])
df_hist['qtd'] = ((df_hist['qtd_voip'])/1000000).round(2)
df_hist['dif'] = ((df_hist['dif'])).round(2)
df_hist['color'] = np.where(df_hist['dif'] < 0, '#e8816e', '#4c60d6')

df_hist['var'] = df_hist['var'].fillna(0)
df_hist['dif'] = df_hist['dif'].fillna(0)

#######################
# 6.2 Histórico Perfil de tráfego
# Dataframe agrupando por perfil de trafego
df_perfil_histx = (df_perfil[['dt_mes', 'perfil_voip', 'qtd_voip']]).groupby(
    ['dt_mes', 'perfil_voip'])['qtd_voip'].sum().reset_index()

df_perfil_histx['perfil'] = df_perfil_histx.perfil_voip.apply(
    lambda x: 'SEM TRAFEGO' if x == 'SEM CDR' else 'COM TRAFEGO'
)

# Criando proporcao
df_perfil_hist = df_perfil_histx.groupby(
    ['dt_mes', 'perfil_voip', 'perfil']).agg({'qtd_voip': 'sum'})
df_perfil_hist['prop'] = (df_perfil_hist.groupby(level=0).apply(
    lambda x: 100*x/x.sum()).reset_index(level=0, drop=True)).round(0)


#######################
# 6.3 Histórico de acessos por tipo de tráfego
# renomeando as colunas

# apagar a coluna que nao irei usar e nao destoar no gráfico
df_voip_traf.drop('ano_mes', axis=1, inplace=True)

df_voip_traf.rename(columns={'qtd_voip_local_ff': 'Local_FF',
                             'qtd_voip_local_fm': 'Local_FM',
                             'qtd_voip_ldn_ff': 'LDN_FF',
                             'qtd_voip_ldn_fm': 'LDN_FM'
                             }, inplace=True)

# Transformando colunas em linhas
df_voip_traf_hist = pd.melt(df_voip_traf, id_vars=['dt_mes'])

#######################
# 6.4 Histórico tráfego entrante e sainte
# Sainte

# aproveitar o df_traf_min
df_traf_min_hist = df_traf_min.copy()

# apagar a coluna que nao irei usar e nao destoar no gráfico
df_traf_min_hist.drop('total_minutos_sainte', axis=1, inplace=True)
df_traf_min_hist.drop('ano_mes', axis=1, inplace=True)

# renomeando as colunas
df_traf_min_hist.rename(columns={'qt_min_local_ff': 'Local_FF',
                                 'qt_min_local_fm': 'Local_FM',
                                 'qt_min_ldn_ff': 'LDN_FF',
                                 'qt_min_ldn_fm': 'LDN_FM',
                                 'qt_min_ngeo': 'NGEO',
                                 'qt_min_ldi': 'LDI',

                                 }, inplace=True)

# Transformando colunas em linhas
df_traf_min_hist = pd.melt(df_traf_min_hist, id_vars=['dt_mes'])

# Entrante
# historico trafego entrante
df_traf_min_ent = df_perfil[['dt_mes', 'qt_min_local_ff_ent', 'qt_min_local_fm_ent',
                             'qt_min_ldn_ff_ent', 'qt_min_ldn_fm_ent', 'qt_min_ldi_ent', 'total_minutos_entrante']]
df_traf_min_ent = df_traf_min_ent.groupby(["dt_mes"]).sum(['qt_min_local_ff_ent', 'qt_min_local_fm_ent',
                                                           'qt_min_ldn_ff_ent', 'qt_min_ldn_fm_ent', 'qt_min_ldi_ent', 'total_minutos_entrante']).reset_index()

# aproveitar o df_traf_min
df_traf_min_hist_ent = df_traf_min_ent.copy()

# apagar a coluna que nao irei usar e nao destoar no gráfico
df_traf_min_hist_ent.drop('total_minutos_entrante', axis=1, inplace=True)

# renomeando as colunas
df_traf_min_hist_ent.rename(columns={'qt_min_local_ff_ent': 'Local_FF',
                                     'qt_min_local_fm_ent': 'Local_FM',
                                     'qt_min_ldn_ff_ent': 'LDN_FF',
                                     'qt_min_ldn_fm_ent': 'LDN_FM',
                                     'qt_min_ngeo_ent': 'NGEO',
                                     'qt_min_ldi_ent': 'LDI'

                                     }, inplace=True)

# Transformando colunas em linhas
df_traf_min_hist_ent = pd.melt(df_traf_min_hist_ent, id_vars=['dt_mes'])

#######################
# 6.5 PIVOT com tráfego entrante e sainte

df_traf_min.drop('ano_mes', axis=1, inplace=True)
# df_traf_min_ent.drop('ano_mes', axis=1, inplace=True)

# total entrante
df_ent = df_traf_min_ent[['dt_mes', 'total_minutos_entrante']]

df_traf_minx = pd.merge(df_traf_min, df_ent, left_on=[
                        'dt_mes'], right_on=['dt_mes'], how='left')
df_traf_minx['total_trafego'] = (
    df_traf_minx['total_minutos_sainte'] + df_traf_minx['total_minutos_entrante']).round(1)

# apagar a coluna que nao irei usar
df_traf_minx.drop('total_minutos_entrante', axis=1, inplace=True)

# Transformando colunas em linhas
df_sai_col = pd.melt(df_traf_minx, id_vars=['dt_mes'])
df_ent_col = pd.melt(df_traf_min_ent, id_vars=['dt_mes'])

df_sai_col['value'] = (df_sai_col['value']).round(1)
df_ent_col['value'] = (df_ent_col['value']).round(1)

# Concat
df_min_pv = pd.concat([df_sai_col, df_ent_col])

# Criar campo order
df_min_pv['order'] = df_min_pv['variable']

# criando ordem das metricas
dic_order = {
    'qt_min_local_ff': 1,
    'qt_min_local_fm': 2,
    'qt_min_ldn_ff': 3,
    'qt_min_ldn_fm': 4,
    'qt_min_ngeo': 5,
    'qt_min_ldi': 6,
    'total_minutos_sainte': 7,
    'qt_min_local_ff_ent': 8,
    'qt_min_local_fm_ent': 9,
    'qt_min_ldn_ff_ent': 10,
    'qt_min_ldn_fm_ent': 11,
    'qt_min_ldi_ent': 12,
    'total_minutos_entrante': 13,
    'total_trafego': 14
}

# Replace
df_min_pv = df_min_pv.replace({'order': dic_order})

# Criando pivot table
pv_df_min_col = pd.pivot_table(df_min_pv, index=['order', 'variable'], aggfunc='sum', columns=[
                               'dt_mes'], values=['value'], fill_value=0)
pv_df_min_col = pv_df_min_col.sort_values(by=['order'], ascending=True)

# *************************************************************************#
###########################################################################
# Construção dos Gráficos
# 5.1 Visao geral da planta
# Metrica criada no Main Panel

# 5.2 Gain/Loss UF
# Metrica criada no Main Panel

#######################
# 5.3 Mapa

# Carregando o arquivo Json com o mapa do Brasil
with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
    Brasil = json.load(response)

state_id_map = {}
for feature in Brasil["features"]:
    feature["id"] = feature["properties"]["sigla"]
    # definindo a informação do gráfico
    state_id_map[feature["properties"]["sigla"]] = feature["id"]

# Criando o mapa
choropleth = px.choropleth_mapbox(
    df_uf,  # database
    locations='uf',  # define os limites no mapa
    geojson=Brasil,  # Coordenadas geograficas dos estados
    color="qtd_voip",  # define a metrica para a cor da escala
    hover_name='uf',  # informação no box do mapa
    hover_data=["uf"],
    # title="Acessos",  # titulo do mapa
    labels=dict(uf="UF", qtd="VOIP"),
    mapbox_style="carto-darkmatter",  # define o style do mapa
    center={"lat": -14, "lon": -55},  # define os limites para plotar
    zoom=2.5,  # zoom inicial no mapa
    color_continuous_scale="greens",  # cor dos estados
    opacity=1  # opacidade da cor do mapa, para aparecer o fundo
)

choropleth.update_layout(

    plot_bgcolor='rgba(0, 0, 0, 0)',
    coloraxis_showscale=False,  # Tira a legenda
    margin=dict(l=0, r=0, t=0, b=0),
    height=500
)

#######################
# 5.4 Por unidade de negocio
un_gr = px.pie(df_un, names='grupo_unidade', values='qtd_voip',
               # height=600, width=600,
               hole=0.5,
               template="plotly_dark",
               color_discrete_sequence=px.colors.sequential.Greens_r)
un_gr.update_traces(hovertemplate=None, textposition='outside',
                    textinfo='percent+label', rotation=50)
un_gr.update_layout(margin=dict(t=50, b=35, l=0, r=0), showlegend=False)
un_gr.add_annotation(dict(x=0.5, y=0.5,  align='center',
                          xref="paper", yref="paper",
                          showarrow=False, font_size=22,
                          text="UN"))

#######################
# 5.5 Por idade
idade = px.pie(df_idade, names='idade', values='qtd_voip',
               # height=300, width=600,
               hole=0.5,
               template="plotly_dark",
               color_discrete_sequence=px.colors.sequential.Greens_r)
idade.update_traces(hovertemplate=None, textposition='outside',
                    textinfo='percent+label', rotation=50)
idade.update_layout(margin=dict(t=50, b=35, l=0, r=0), showlegend=False)
idade.add_annotation(dict(x=0.5, y=0.5,  align='center',
                          xref="paper", yref="paper",
                          showarrow=False, font_size=22,
                          text="Idade"))

#######################
# 5.6 Representatividade por regiao

reg_uf = px.sunburst(df_uf_reg, path=['regiao', 'uf'], values='qtd_voip',
                     labels=dict(regiao="Região", qtd_voip="VOIP"),
                     template="plotly_dark",
                     height=500,  # altura
                     width=500,  # largura
                     color_discrete_sequence=px.colors.sequential.Greens_r)
reg_uf.update_traces(textinfo="label+percent parent")

#######################
# 5.7 Trafego
perfil_gr = px.sunburst(df_voz,
                        path=['perfil', 'perfil_voip'],
                        values='qtd_voip',
                        labels=dict(labels=" Trafego",
                                    parent="Trafego detalhado", QTD_VOIP="VOIP"),
                        hover_name='perfil',
                        template="plotly_dark",
                        color_discrete_sequence=px.colors.sequential.Greens_r
                        )
perfil_gr.update_traces(textinfo='label+value+percent root')

#######################
# 5.8 Acessos por tipo de Trafego
# Quantidade de VOIPs por tipo de tráfego
voip_tipo = px.pie(df_voip_traf_max, names='variable', values='value',
                   labels=dict(variable="Tráfego", value="VOIP"),
                   # height=500, width=500,
                   hole=0.5,
                   template="plotly_dark",
                   color_discrete_sequence=px.colors.sequential.Greens_r)
voip_tipo.update_traces(textposition='outside',
                        textinfo='percent+value+label', rotation=50)
voip_tipo.update_layout(margin=dict(t=50, b=35, l=0, r=0), showlegend=False)
voip_tipo.add_annotation(dict(x=0.5, y=0.5,  align='center',
                              xref="paper", yref="paper",
                              showarrow=False, font_size=22,
                              text="Qtd Voip"))

#######################
# 5.9 Minutos por tipo de Trafego
min_traf = px.pie(df_traf_min_max, names='variable', values='value',
                  labels=dict(variable="Tráfego", value="Minutos"),
                  # height=500, width=500,
                  hole=0.5,
                  template="plotly_dark",
                  color_discrete_sequence=px.colors.sequential.Greens_r)
min_traf.update_traces(textposition='outside',
                       textinfo='percent+value+label', rotation=50)
min_traf.update_layout(margin=dict(t=50, b=35, l=0, r=0), showlegend=False)
min_traf.add_annotation(dict(x=0.5, y=0.5,  align='center',
                        xref="paper", yref="paper",
                        showarrow=False, font_size=22,
                        text="Minutos"))

#######################
# 6.1 Historico planta
# Historico 2000 a 2023
# Historico de acessos e diferença
plt_his = px.line(df_hist, x='dt_base', y='qtd',
                  # height=400, width=800, #altura x largura
                  labels=dict(dt_base="dt_base",  qtd="VOIP (MM)"), text="qtd",
                  color_discrete_sequence=["#85d338"],
                  line_shape="spline", markers=True, template="plotly_dark")

plt_his.update_traces(line_width=2, textposition='top center')
# fig.update_yaxes(ticksuffix="MM", showgrid=True)
plt_his.update_yaxes(showticklabels=False)
plt_his.update_xaxes(showgrid=False)
plt_his.update_yaxes(showgrid=False)
plt_his.update_layout(xaxis=dict(linecolor='rgba(0,0,0,1)', tickmode='array',
                      tickvals=df_hist['dt_base'], ticktext=df_hist['dt_base']))
plt_his.update_layout(
    autosize=False,
    width=600,
    height=300,
    margin=dict(
        l=20,
        r=20,
        b=20,
        t=10
    ),
)


plt_his2 = px.bar(df_hist, x="dt_base", y="dif", title="Diferença MxM", template="plotly_dark", text_auto=True,
                  # height=300, width=600,  #largura
                  labels=dict(dt_base="dt_base",  qtd="VOIP", dif='Diferença', var='Variação'), hover_data=['dt_base', 'dif', 'var']
                  )
plt_his2.update_traces(textangle=0, textfont_size=12, textposition='outside',
                       cliponaxis=False, marker_color=df_hist["color"])
plt_his2.update_yaxes(showticklabels=False, showgrid=False,
                      visible=False, fixedrange=True)
plt_his2.update_xaxes(showgrid=False, visible=False, fixedrange=True)
# fig2.update_layout(xaxis = dict(tickmode = 'array', tickvals = df_hist['dt_base'],ticktext = df_hist['dt_base']))
plt_his2.update_layout(
    autosize=False,
    width=600,
    height=250,
    margin=dict(
        l=20,
        r=20,
        b=20,
        t=50
    ),
)

#######################
# 6.2 Histórico Perfil de tráfego
hist_perfil = px.bar(df_perfil_hist.reset_index(), x='dt_mes', y='prop', color='perfil_voip',
                     labels=dict(dt_mes="Ano/Mes", perfil_voip="Perfil VOIP",
                                 prop="Proporção(%)", qtd_voip="VOIP"),
                     hover_data=['dt_mes', 'perfil_voip', 'prop', 'qtd_voip'],
                     color_discrete_sequence=px.colors.sequential.Greens_r,
                     template="plotly_white", text="perfil_voip"
                     )
# the y-axis is in percent
hist_perfil.update_yaxes(ticksuffix="%", showgrid=True)

#######################
# 6.3 Histórico de acessos por tipo de tráfego
# Quantidade de Acessos por tipo de tráfego
hist_voip_t = px.line(df_voip_traf_hist, x='dt_mes', y='value', color='variable',
                      markers=True,
                      # height=600, width=800, #altura x largura
                      line_shape="spline",
                      template="plotly_dark",
                      render_mode="svg",
                      labels=dict(dt_mes="Ano e mês", value="Acessos",
                                  variable="Tipo de tráfego")
                      )

# 6.4 Histórico tráfego entrante e sainte
# Sainte
# Quantidade de minutos por tipo de tráfego sainte

traf_sainte = px.line(df_traf_min_hist, x='dt_mes', y='value', color='variable',
                      markers=True,
                      # height=600, width=800, #altura x largura
                      line_shape="spline",
                      template="plotly_dark",
                      render_mode="svg",
                      labels=dict(dt_mes="Ano e mês", value="Minutos",
                                  variable="Tipo de tráfego")
                      )

# Entrante
traf_entrante = px.line(df_traf_min_hist_ent, x='dt_mes', y='value', color='variable',
                        markers=True,
                        # height=600, width=800, #altura x largura
                        line_shape="spline",
                        template="plotly_dark",
                        render_mode="svg",
                        labels=dict(dt_mes="Ano e mês",
                                    value="Minutos", variable="Tipo de tráfego")
                        )

# 6.5 Pivot
pv_traf = px.imshow(pv_df_min_col,
                    labels=dict(x="dt_mes", y="variable", color="value"),
                    y=['qt_min_local_ff', 'qt_min_local_fm', 'qt_min_ldn_ff', 'qt_min_ldn_fm', 'qt_min_ngeo', 'qt_min_ldi', 'total_minutos_sainte',
                        'qt_min_local_ff_ent', 'qt_min_local_fm_ent', 'qt_min_ldn_ff_ent', 'qt_min_ldn_fm_ent', 'qt_min_ldi_ent', 'total_minutos_entrante', 'total_trafego'],
                    x=['2024-04-01', '2024-05-01', '2024-06-01',
                       '2024-07-01', '2024-08-01', '2024-09-01', '2024-10-01'],
                    # labels=dict(ano="Ano", marca="Operadora", qtd="Reclamações"),
                    color_continuous_scale="YlOrRd",
                    text_auto=True,
                    template="plotly_dark",
                    height=550,  # altura
                    width=950,  # largura
                    )

pv_traf.update_xaxes(side="top")


# **************************************************************************#
############################################################################
# Dashboard Main Panel


st.markdown("# Perfil ")

with st.expander("Visão Geral, 202410", expanded=True):

    col = st.columns((2.2, 4.3, 4), gap='medium')

    with col[0]:
        st.markdown('#### Total Acessos')

        st.metric(label=str((df_res_plt.dt_base.values[0])), value=str(
            (df_res_plt.acessos.values[0]))+" M", delta=str(var_ano)+"K")

        st.markdown('#### Ganhos/Perdas')
        st.metric(label=str((ind_gain.nome_estado.values[0])), value=str(
            (ind_gain.qtd_voip_x.values[0])), delta=str((ind_gain.dif.values[0])))

        st.metric(label=str((ind_loss.nome_estado.values[0])), value=str(
            (ind_loss.qtd_voip_x.values[0])), delta=str((ind_loss.dif.values[0])))

    with col[1]:
        st.markdown('#### Mapa')
        st.plotly_chart(choropleth, use_container_width=True)

    with col[2]:
        st.markdown('#### Top States')
        st.dataframe(
            df_uf_hist, height=500,
            column_order=("flag", "uf", "20240930", "historico"),
            column_config={
                "flag": st.column_config.ImageColumn(" ", width="small"),
                "uf": "UF",
                "20240930": "202409",
                "historico": st.column_config.LineChartColumn(
                    "Histórico"
                ),
            },
            hide_index=True,
        )

with st.expander("Informações Gerais, 202410", expanded=True):

    col2 = st.columns((3, 3, 3), gap='medium')

    with col2[0]:
        st.plotly_chart(un_gr, use_container_width=True)

    with col2[1]:
        st.plotly_chart(idade, use_container_width=True)

    with col2[2]:
        st.plotly_chart(reg_uf, use_container_width=True)


with st.expander("Tráfego, 202410", expanded=True):

    col3 = st.columns((3, 3.5, 4), gap='medium')

    with col3[0]:
        st.plotly_chart(perfil_gr, use_container_width=True)

    with col3[1]:
        st.plotly_chart(voip_tipo, use_container_width=True)

    with col3[2]:
        st.plotly_chart(min_traf, use_container_width=True)

st.markdown("# Perfil Histórico")
st.markdown("### Visão Acessos")

with st.expander("Planta, 202404-202410", expanded=True):
    st.plotly_chart(plt_his, use_container_width=True)
    st.plotly_chart(plt_his2, use_container_width=True)

with st.expander("Perfil de tráfego, 202404-202410", expanded=True):
    st.plotly_chart(hist_perfil, use_container_width=True)

with st.expander("Acessos por tipo de tráfego, 202404-202410", expanded=True):
    st.plotly_chart(hist_voip_t, use_container_width=True)

st.markdown("### Tráfego em Minutos")

with st.expander("Tráfego Sainte, 202404-202410", expanded=True):
    st.plotly_chart(traf_sainte, use_container_width=True)

with st.expander("Tráfego Entrante, 202404-202410", expanded=True):
    st.plotly_chart(traf_entrante, use_container_width=True)

with st.expander("Pivot Tráfego, 202404-202410", expanded=True):
    st.plotly_chart(pv_traf, use_container_width=True)
