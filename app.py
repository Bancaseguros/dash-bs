import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
from plotly.graph_objs import *
import plotly.plotly as py
import pandas as pd
import numpy as np
import calendar
import itertools
import plotly
import os

#--------------------------- APP AND SERVER CONFIG
myvar = [['bancaseguros', '2017bancaseguros']]
app = dash.Dash(__name__)
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')
auth = dash_auth.BasicAuth(app, myvar)
#---------------------------------------------------------

#--------------------------- DATABASES IMPORTS AND ADJUSTMENTS

base = pd.read_csv('https://raw.githubusercontent.com/Bancaseguros/Dashboard-Seguimiento/master/bancasegurosJunSep2.csv', delimiter = ',', encoding = 'latin-1')
#base = pd.read_csv('https://raw.githubusercontent.com/nicolasescobar0325/csv-tables/master/bancasegurosJunSep2.csv', delimiter = ',', encoding = 'latin-1')
del base['Unnamed: 0']
base['FECHA_APERTURA'] = pd.to_datetime(base['FECHA_APERTURA'])
base['FECHA_APERTURA'] = pd.to_datetime(base['FECHA_APERTURA'])
base['numeroMES'] = base['FECHA_APERTURA'].dt.month
base['MES'] = base['numeroMES'].apply(lambda x: calendar.month_abbr[x])

oficinas = pd.read_csv('https://raw.githubusercontent.com/nicolasescobar0325/csv-tables/master/oficinas.csv', delimiter = ',', encoding = 'latin-1')
jerarquias = pd.read_csv('https://raw.githubusercontent.com/nicolasescobar0325/csv-tables/master/jerarquias1.csv', delimiter = ';', encoding = 'latin-1')

options_reg = oficinas['REGIONAL'].unique()
options_sgro = ('ACCIDENTES_PERSONALES', 'DAVIDA', 'DESEMPLEO_FIJO', 'DESEMPLEO_HIPOTECARIO', 'DESEMPLEO_LIBRANZA', 'DESEMPLEO_TDC', 'DESEMPLEO_VEHICULO',
    'HOGAR', 'INCENDIO_TERREMOTO_REINV', 'PROTECCION_TARJETAS', 'RENTA_DIARIA', 'SOAT', 'TRANQUILIDAD_MUJER', 'VEHICULO', 'VIDA_DEUDORES_REINV')
options_inter = base['TIPO_OPERACION'].unique()
options_mes = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

#---------------------------------------------------------

#--------------------------- APP LAYOUT (HTML + DCC)

app.layout = html.Div(style = {'height': '100%', 'min-width': '100%', 'margin': '-8px'}, children =[
    html.Div(style = {'height': '100%', 'background-color': '#111111', 'box-shadow': '4px 5px 9px -3px rgba(102,102,102,1)', 'white-space': 'nowrap', 'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '14'}, children = [
        html.Div(style = {'padding-bottom': '15px', 'overflow': 'visible'}, children = [
            html.Div(style = {'width': '22%', 'float': 'left', 'padding-left': '15px', 'padding-right': '15px'}, children = [
                html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione regional:'),
                dcc.Dropdown(id ='reg-drop', options = [{'label': i, 'value': i} for i in options_reg], value = 'TODAS', clearable = False)
                ]),
            html.Div(style = {'width': '22%', 'float': 'left', 'padding-left': '15px', 'padding-right': '15px'}, children = [
                html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione departamento:'),
                dcc.Dropdown(id ='dpto-drop', clearable = False)
                ]),
            html.Div(style = {'width': '22%', 'float': 'left', 'padding-left': '15px', 'padding-right': '15px'}, children = [
                html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione ciudad:'),
                dcc.Dropdown(id ='ciud-drop', clearable = False)
                ]),
            html.Div(style = {'width': '22%', 'float': 'left', 'padding-left': '15px', 'padding-right': '15px'}, children = [
                html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione oficina:'),
                dcc.Dropdown(id ='ofic-drop', clearable = False)
                ])
            ]),
        html.Div(style = {'position': 'relative', 'overflow': 'visible'}, children = [
            html.Div(style = {'width': '22%', 'float': 'left', 'padding-left': '15px', 'padding-right': '15px'}, children = [
                html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione seguro:'),
                dcc.Dropdown(id ='sgro-drop', options = [{'label': i, 'value': i} for i in options_sgro], value = 'DAVIDA', clearable = False)
                ]),
            html.Div(style = {'width': '70%', 'float': 'left', 'padding-left': '15px', 'padding-right': '15px'}, children = [
                html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione un rango de fechas:'),
                dcc.RangeSlider(id = 'mes-range', marks = options_mes , min=1, max=12, value=[6, 9])
                ])
            ]),
        html.Div(style = {'width': '95%', 'padding-bottom': '15px', 'padding-top': '2px', 'padding-left': '15px', 'padding-right': '15px', 'overflow': 'visible', 'clear':'both'}, children = [
            html.P(style = {'color': '#ffffff', 'font-family': 'Helvetica', 'font-size': '15'}, children = 'Seleccione interacciones:'),
            dcc.Dropdown(id = 'inter-drop', options = [{'label': i, 'value': i} for i in options_inter], multi = True, clearable = False)
            ])
        ]),
    html.Div(style = {'max-width': '100%'}, children =[
        html.Div(style = { 'width': '100%', 'height': '100%', 'margin': '0px', 'overflow': 'hidden'}, children = [
            html.Div(style = { 'width': '48%', 'height': '100%', 'margin': '0px', 'float': 'left'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-1-text'),
                dcc.Graph(id='graph-1', animate = False, style = {'height': '320px', 'width': '95%', 'margin': 'auto'}, config={'displayModeBar': False})
                ]),
            html.Div(style = { 'width': '25%', 'height': '100%', 'margin': '0px', 'float': 'left'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-2a-text'),
                dcc.Graph(id='graph-2a', animate = False, style = {'height': '140px', 'width': '95%', 'margin': 'auto'}, config={'displayModeBar': False}),
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-2b-text'),
                dcc.Graph(id='graph-2b', animate = False, style = {'height': '140px', 'width': '95%', 'margin': 'auto'}, config={'displayModeBar': False})
                ]),
            html.Div(style = { 'width': '25%', 'height': '100%', 'margin': '0px', 'float': 'left'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-3a-text'),
                dcc.Graph(id='graph-3a', animate = False, style = {'height': '140px', 'width': '95%', 'margin': 'auto'}, config={'displayModeBar': False}),
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-3b-text'),
                dcc.Graph(id='graph-3b', animate = False, style = {'height': '140px', 'width': '95%', 'margin': 'auto'}, config={'displayModeBar': False})
                ]),
            ]),
        html.Br(),
        html.Br(),
        html.Div(style = { 'max-width': '100%', 'height': '100%', 'margin': '0px'}, children = [
            html.Div(style = { 'width': '100%', 'height': '100%', 'margin': '0px'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-4-text'),
                dcc.Graph(id='graph-4', animate = False, style = {'height': '160px', 'width': '100%', 'margin': 'auto'}, config={'displayModeBar': False})
                ])
            ]),
        html.Div(style = { 'max-width': '100%', 'height': '100%', 'margin': '0px'}, children = [
            html.Div(style = { 'width': '100%', 'height': '100%', 'margin': '0px'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-5-text'),
                dcc.Graph(id='graph-5', animate = False, style = {'height': '160px', 'width': '100%', 'margin': 'auto'}, config={'displayModeBar': False})
                ])
            ]),
        html.Br(),
        html.Br(),
        html.Div(style = { 'width': '100%', 'height': '100%', 'margin': '0px', 'overflow': 'hidden'}, children = [
            html.Div(style = { 'width': '80%', 'height': '100%', 'margin': 'auto'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-6-text'),
                dcc.Graph(id = 'graph-6', config={'displayModeBar': False})
                ])
            ]),
        html.Br(),
        html.Br(),
        html.Div(style = { 'width': '100%', 'height': '100%', 'margin': '0px', 'overflow': 'hidden'}, children = [
            html.Div(style = { 'width': '80%', 'height': '100%', 'margin': 'auto'}, children = [
                html.P(style = {'color': '#7f7f7f', 'font-family': 'Helvetica', 'font-size': '16', 'text-align': 'center'}, id = 'graph-7-text'),
                dcc.Graph(id = 'graph-7', config={'displayModeBar': False})
                ])
            ]),
        html.Br()
        ])
    ])

#---------------------------------------------------------

#--------------------------- DEPENDENT DROPDOWNS CALLBACKS

@app.callback(
    dash.dependencies.Output('dpto-drop', 'options'),
    [dash.dependencies.Input('reg-drop', 'value')])
def set_cities_options(selected_reg):
    filtro = oficinas[oficinas['REGIONAL'] == selected_reg]
    return [{'label': i, 'value': i} for i in filtro['DEPARTAMENTO'].unique()]

@app.callback(
    dash.dependencies.Output('dpto-drop', 'value'),
    [dash.dependencies.Input('reg-drop', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    dash.dependencies.Output('ciud-drop', 'options'),
    [dash.dependencies.Input('dpto-drop', 'value')])
def set_cities_options(selected_dpto):
    filtro = oficinas[oficinas['DEPARTAMENTO'] == selected_dpto]
    return [{'label': i, 'value': i} for i in filtro['CIUDAD'].unique()]

@app.callback(
    dash.dependencies.Output('ciud-drop', 'value'),
    [dash.dependencies.Input('dpto-drop', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    dash.dependencies.Output('ofic-drop', 'options'),
    [dash.dependencies.Input('ciud-drop', 'value')])
def set_cities_options(selected_dpto):
    filtro = oficinas[oficinas['CIUDAD'] == selected_dpto]
    return [{'label': i, 'value': i} for i in filtro['NOMBRE_OFICINA'].unique()]

@app.callback(
    dash.dependencies.Output('ofic-drop', 'value'),
    [dash.dependencies.Input('ciud-drop', 'options')])
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    dash.dependencies.Output('inter-drop', 'options'),
    [dash.dependencies.Input('sgro-drop', 'value')])
def set_cities_options(selected_sgro):
    jerarquias= pd.read_csv('https://raw.githubusercontent.com/nicolasescobar0325/csv-tables/master/jerarquias1.csv', delimiter = ';', encoding = 'latin-1')
    jerarquias = jerarquias[jerarquias[selected_sgro] == True]
    jerarquias = jerarquias[['TIPO_OPERACION']]

    return [{'label': i, 'value': i} for i in jerarquias['TIPO_OPERACION'].unique()]

@app.callback(
    dash.dependencies.Output('inter-drop', 'value'),
    [dash.dependencies.Input('sgro-drop', 'value')])
def set_cities_value(selected_sgro):
    jerarquias= pd.read_csv('https://raw.githubusercontent.com/nicolasescobar0325/csv-tables/master/jerarquias1.csv', delimiter = ';', encoding = 'latin-1')
    jerarquias = jerarquias[jerarquias[selected_sgro] == True]
    jerarquias = jerarquias['TIPO_OPERACION'].tolist()

    return jerarquias

#---------------------------------------------------------

#--------------------------- DIV'S TEXT CALLBACKS

@app.callback(
    dash.dependencies.Output('graph-1-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    graph1text = ''

    if selected_reg == 'TODAS':
        graph1text = 'Participación de Regionales'
    elif selected_dpto == 'TODAS':
        graph1text = 'Participación por Departamento'
    elif selected_ciud == 'TODAS':
        graph1text = 'Participación por Ciudad'
    elif selected_ofic == 'TODAS':
        graph1text = 'Participación por Oficina'
    else:
        graph1text = 'Participación por Oficina'

    return graph1text

@app.callback(
    dash.dependencies.Output('graph-2a-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Valor total primas ($)'

@app.callback(
    dash.dependencies.Output('graph-2b-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Cantidad de pólizas emitidas'

@app.callback(
    dash.dependencies.Output('graph-3a-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Interacciones Factibles'

@app.callback(
    dash.dependencies.Output('graph-3b-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Penetración (%)'

@app.callback(
    dash.dependencies.Output('graph-4-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Pólizas emitidas por tipo de interacción (%)'

@app.callback(
    dash.dependencies.Output('graph-5-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Tipo de interacción respecto al total de interacciones (%)'

@app.callback(
    dash.dependencies.Output('graph-6-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Mejores oficinas en Penetración'

@app.callback(
    dash.dependencies.Output('graph-7-text', 'children'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def set_display_children(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):

    return 'Peores oficinas en Penetración'

#---------------------------------------------------------

#--------------------------- GRAPH 1 - SCATTER CHART

@app.callback(
    dash.dependencies.Output('graph-1', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    colores = ['#C49BA8', '#E57661', '#F8C58C', '#F8E7A2', '#86DDB2', '#7FADA9', '#588E95', '#ADD96C', '#4EA64B']
    val_selected_sgro = 'VAL_' + selected_sgro
    crit_selected_sgro = 'crit_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    base_filtro = base_filtro[base_filtro['REGIONAL'] != 'OTRA']
    base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] != 'OTRA']
    base_filtro = base_filtro[base_filtro['CIUDAD'] != 'OTRA']
    base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] != 'OTRA']

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', selected_sgro, crit_selected_sgro, val_selected_sgro]].groupby(['REGIONAL'], as_index = False).sum()
        base_filtro['labels'] = base_filtro['REGIONAL'].astype(str)
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', selected_sgro, crit_selected_sgro, val_selected_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro['labels'] = base_filtro['DEPARTAMENTO'].astype(str)
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro, crit_selected_sgro, val_selected_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro['labels'] = base_filtro['CIUDAD']
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_selected_sgro, val_selected_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro['labels'] = base_filtro['NOMBRE_OFICINA']


    base_filtro['pen_sgro'] = base_filtro[selected_sgro]*100/base_filtro[crit_selected_sgro]
    base_filtro['sgro_TXT'] = base_filtro[selected_sgro].astype(str)
    base_filtro['VAL_sgro_TXT'] = base_filtro[val_selected_sgro].astype(str)
    base_filtro['sgro_TXT'] = base_filtro['labels'] + '<br>' + base_filtro['sgro_TXT'] + ' pólizas'
    base_filtro['VAL_sgro_TXT'] = base_filtro['labels'] + '<br>$' + base_filtro['VAL_sgro_TXT']

    base_filtro['selected_sgro_t'] = base_filtro[selected_sgro].astype(str)
    base_filtro['val_selected_sgro_t'] = base_filtro[val_selected_sgro].astype(str)

#--

    if base_filtro[selected_sgro].max() < 100:
        base_filtro['size'] = base_filtro[selected_sgro]
    elif base_filtro[selected_sgro].max() < 1000:
        base_filtro['size'] = base_filtro[selected_sgro]/10
    elif base_filtro[selected_sgro].max() < 10000:
        base_filtro['size'] = base_filtro[selected_sgro]/100
    elif base_filtro[selected_sgro].max() < 100000:
        base_filtro['size'] = base_filtro[selected_sgro]/1000

    if base_filtro[val_selected_sgro].max() < 1000000:
        base_filtro['size_val'] = base_filtro[val_selected_sgro]/10000
    elif base_filtro[val_selected_sgro].max() < 10000000:
        base_filtro['size_val'] = base_filtro[val_selected_sgro]/100000
    elif base_filtro[val_selected_sgro].max() < 100000000:
        base_filtro['size_val'] = base_filtro[val_selected_sgro]/1000000
    elif base_filtro[val_selected_sgro].max() < 1000000000:
        base_filtro['size_val'] = base_filtro[val_selected_sgro]/10000000
    elif base_filtro[val_selected_sgro].max() < 10000000000:
        base_filtro['size_val'] = base_filtro[val_selected_sgro]/100000000

    multip = base_filtro[selected_sgro].max().astype(str)[0]
    v_multip = base_filtro[val_selected_sgro].max().astype(str)[0]

    if multip == '1':
        base_filtro['multip'] = 8
    elif multip == '2':
        base_filtro['multip'] = 4
    elif multip == '3':
        base_filtro['multip'] = 2.5
    elif multip == '4':
        base_filtro['multip'] = 2
    elif multip == '5':
        base_filtro['multip'] = 1.5
    elif multip == '6':
        base_filtro['multip'] = 1.3
    elif multip == '7':
        base_filtro['multip'] = 1.1
    else:
        base_filtro['multip'] = 1


    if v_multip == '1':
        base_filtro['v_multip'] = 8
    elif v_multip == '2':
        base_filtro['v_multip'] = 4
    elif v_multip == '3':
        base_filtro['v_multip'] = 2.5
    elif v_multip == '4':
        base_filtro['v_multip'] = 2
    elif v_multip == '5':
        base_filtro['v_multip'] = 1.5
    elif v_multip == '6':
        base_filtro['v_multip'] = 1.3
    elif v_multip == '7':
        base_filtro['v_multip'] = 1.1
    else:
        base_filtro['v_multip'] = 1

    trace1 = Scatter(
    x = base_filtro[crit_selected_sgro],
    y = base_filtro['pen_sgro'],
    text = base_filtro['sgro_TXT'],
    name = '',
    mode = 'markers',
    opacity = 0.6,
    marker = Marker(color = '#F46D43', size = base_filtro['size']*base_filtro['multip']),
    visible = True,
    hoverinfo = 'text'
    )

    trace2 = Scatter(
    x = base_filtro[crit_selected_sgro],
    y = base_filtro['pen_sgro'],
    text = base_filtro['VAL_sgro_TXT'],
    name = '',
    mode = 'markers',
    opacity = 0.6,
    marker = Marker(color = '#1A9850', size = base_filtro['size_val']*base_filtro['v_multip']),
    visible = False,
    hoverinfo = 'text'
        )

    data = Data([trace1, trace2])

    updatemenus = list([
        dict(type="buttons",
             showactive= True,
             buttons=list([
                dict(label = 'Pólizas',
                     method = 'update',
                     args = [{'visible': [True, False]}]),
                dict(label = 'Primas ($)',
                     method = 'update',
                     args = [{'visible': [False, True]}])
            ]),
             x = '0.75',
             xanchor = 'right',
             y = '1',
             yanchor = 'top',
             direction = 'right'
        )
    ])

    layout = Layout(
    xaxis = dict(title = 'Interacciones Factibles', autorange = True, titlefont = dict(size = 14, family = 'Helvetica', color = '#7f7f7f')),
    yaxis = dict(title = '% Penetración', autorange = True, titlefont = dict(size = 14, family = 'Helvetica', color = '#7f7f7f')),
    margin = Margin(t = 20, b = 70, l = 70, r= 20, pad = 4), #20,80,70,50
#    paper_bgcolor = '#7f7f7f',
#    plot_bgcolor = '#c7c7c7',
    updatemenus = updatemenus
    )

    return Figure(data=data, layout=layout)

#---------------------------------------------------------

#--------------------------- GRAPH 2-A "VALOR PRIMAS"

@app.callback(
    dash.dependencies.Output('graph-2a', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    val_selected_sgro = 'VAL_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES',], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
    else:
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] == selected_ofic]

    trace1 = Scatter(
    x = base_filtro['MES'],
    y = base_filtro[val_selected_sgro],
    text='Valor Primas ($)',
    name='',
    marker={'symbol': 'star', 'size': "8", 'color': '#ed1c27'},
    mode="markers+lines"
    )

    layout = Layout(
    title = '',
    titlefont= {'family': 'Helvetica', 'size': '16', 'color': '#7f7f7f'},
    xaxis={'title': ''},
    yaxis= dict(range = [0, base_filtro[val_selected_sgro].max()*1.1], title='', showgrid=False, zeroline=False, showline=False, showticklabels=True),
    margin={'l': 40, 'b': 50, 't': 0, 'r': 30},
    showlegend = False
    )

    data= Data([trace1])

    return Figure(data=data, layout=layout)

#---------------------------------------------------------

#--------------------------- GRAPH 2-B "PÓLIZAS VENDIDAS"

@app.callback(
    dash.dependencies.Output('graph-2b', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    val_selected_sgro = 'VAL_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES',], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
    else:
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, val_selected_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] == selected_ofic]

    trace1 = Bar(
    x = base_filtro['MES'],
    y = base_filtro[selected_sgro],
    text = 'Pólizas vendidas',
    name = '',
    marker =  {'color': '#338d11'},
    )

    layout = Layout(
    title = '',
    titlefont = {'family': 'Helvetica', 'size': '16', 'color': '#7f7f7f'},
    xaxis = {'title': ''},
    yaxis = dict(range = [0, base_filtro[selected_sgro].max()*1.1], title='', showgrid=False, zeroline=False, showline=False, showticklabels=True),
    margin = {'l': 40, 'b': 50, 't': 0, 'r': 30},
    showlegend = False
    )

    data = Data([trace1])

    return Figure(data = data, layout = layout)

#---------------------------------------------------------

#--------------------------- GRAPH 3-A "VALOR PRIMAS"

@app.callback(
    dash.dependencies.Output('graph-3a', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    crit_sgro = 'crit_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION'], as_index = False).sum()
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES'], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'TIPO_OPERACION'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL'], as_index = False).sum()
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
    else:
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] == selected_ofic]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA'], as_index = False).sum()

    base_filtro['pen_sgro'] = np.round(base_filtro[selected_sgro]*100/base_filtro[crit_sgro], decimals = 1, out = None)
    base_filtro_g['pen_sgro'] = np.round(base_filtro_g[selected_sgro]*100/base_filtro_g[crit_sgro], decimals = 1, out = None)
    base_filtro['txt_pen_sgro'] = base_filtro['pen_sgro'].astype(str)
    base_filtro['txt_pen_sgro'] = 'Pen. ' + base_filtro['txt_pen_sgro'] + '%'
    base_filtro_g['txt_pen_sgro_g'] = base_filtro_g['pen_sgro'].astype(str)
    base_filtro_g['txt_pen_sgro_g'] = 'Pen. ' + base_filtro_g['txt_pen_sgro_g'] + '%'

    trace1 = Scatter(
    x = base_filtro_g['MES'],
    y = base_filtro_g[crit_sgro],
    name = 'Interacciones',
    marker = {'color': '#ed1c27'},
    mode = 'lines'
    )

    layout = Layout(
    title = '',
    titlefont= {'family': 'Helvetica', 'size': '16', 'color': '#7f7f7f'},
    xaxis = {'title': ''},
    yaxis = dict(rangemode = 'tozero', range = [0, base_filtro_g[crit_sgro].max()*1.3], title='', showgrid=False, zeroline=False, showline=False, showticklabels=True),
    margin={'l': 40, 'b': 50, 't': 0, 'r': 30},
    showlegend = False
    )

    data= Data([trace1])

    return Figure(data=data, layout=layout)

#---------------------------------------------------------

#--------------------------- GRAPH 3-B "PÓLIZAS VENDIDAS"

@app.callback(
    dash.dependencies.Output('graph-3b', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    crit_sgro = 'crit_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION'], as_index = False).sum()
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES'], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'TIPO_OPERACION'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL'], as_index = False).sum()
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
    else:
        base_filtro = base_filtro[['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] == selected_ofic]
        base_filtro_g = base_filtro[['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['FECHA_APERTURA', 'MES', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA'], as_index = False).sum()

    base_filtro['pen_sgro'] = np.round(base_filtro[selected_sgro]*100/base_filtro[crit_sgro], decimals = 1, out = None)
    base_filtro_g['pen_sgro'] = np.round(base_filtro_g[selected_sgro]*100/base_filtro_g[crit_sgro], decimals = 1, out = None)
    base_filtro['txt_pen_sgro'] = base_filtro['pen_sgro'].astype(str)
    base_filtro['txt_pen_sgro'] = 'Pen. ' + base_filtro['txt_pen_sgro'] + '%'
    base_filtro_g['txt_pen_sgro_g'] = base_filtro_g['pen_sgro'].astype(str)
    base_filtro_g['txt_pen_sgro_g'] = base_filtro_g['txt_pen_sgro_g'] + '%'

    trace1 = Scatter(
    x = base_filtro_g['MES'],
    y = base_filtro_g['pen_sgro'],
    name = 'Penetración',
    marker = {'color': '#0B877D', 'size': "5"},
    mode = 'markers+lines+text',
    textposition = 'top',
    text = base_filtro_g['txt_pen_sgro_g'],
    hoverinfo = 'none'
    )

    layout = Layout(
    title = '',
    titlefont = {'family': 'Helvetica', 'size': '16', 'color': '#7f7f7f'},
    xaxis = dict(title = ''),
    yaxis= dict(rangemode = 'tozero', range = [0, base_filtro_g['pen_sgro'].max()*2], title='', showgrid=False, zeroline=False, showline=False, showticklabels = False),
    margin = {'l': 40, 'b': 50, 't': 0, 'r': 30},
    showlegend = False
    )

    data = Data([trace1])

    return Figure(data = data, layout = layout)

#---------------------------------------------------------

#--------------------------- GRAPH 4 - STACKED BAR

@app.callback(
    dash.dependencies.Output('graph-4', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]
    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', selected_sgro]].groupby(['TIPO_OPERACION'], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', selected_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', selected_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', selected_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
    else:
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] == selected_ofic]

    base_filtro = base_filtro.sort_values(selected_sgro, ascending = False)
    base_filtro = base_filtro.reset_index()
    annotation = np.round((base_filtro[selected_sgro]*100/base_filtro[selected_sgro].sum()), decimals = 1, out = None)
    annotation = np.where(annotation >= 2.4, annotation.astype(str)+'%', '')

    color = {'ACTIVACION TDC': '#0B877D', 'APERTURAS PASIVO': '#126872', 'APROBACIONES CREDITOS': '#2D587B', 'DESEMBOLSOS CREDITOS': '#184169', 'OTRA': '#FFD351', 'PREAPROBADOS': '#121C25', 'SOLICITUDES': '#13314D', 'TRANSACCIONES CAJA': '#C9283E', 'TELEMERCADEO': 'rgb(69,117,180)'}

    data = []
    for i in base_filtro['TIPO_OPERACION']:
        data.append(
            Bar(
                y = 1,
                x = base_filtro[base_filtro['TIPO_OPERACION'] == i][selected_sgro],
                hoverinfo= 'text',
                marker = dict(color = color[i]),
                name = i,
                text =  base_filtro[base_filtro['TIPO_OPERACION'] == i][selected_sgro].astype(str) + ' pólizas',
                orientation = 'h'
            )
        )

    annotations = []
    acumulado = 0

    for i in range(0,len(base_filtro)):
        annotations.append(
            dict(
                xref='x',
                yref='y',
                x = ((base_filtro[selected_sgro][i] / 2) + acumulado),
                y=0,
                text = annotation[i],
                font = dict(family='Helvetica', size=12, color='rgb(248, 248, 255)'),
                showarrow=False
                )
           )
        acumulado = acumulado + base_filtro[selected_sgro][i]

    layout = Layout(
        barmode = 'stack',
        title = '',
        xaxis = dict({'title':''}, showgrid=False, showticklabels = False),
        yaxis = dict({'title':''}, showgrid=False, showticklabels = False),
        margin = {'l': 40, 'b': 100, 't': 0, 'r': 30},
        showlegend = True,
#       paper_bgcolor = '#7f7f7f',
#       plot_bgcolor = '#c7c7c7',
        legend = dict(orientation = 'h')
        )

    layout['annotations'] = annotations

    return Figure(data = data, layout = layout)

#---------------------------------------------------------

#--------------------------- GRAPH 5 - STACKED BAR 2

@app.callback(
    dash.dependencies.Output('graph-5', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_figure(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    crit_sgro = 'crit_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]
    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', crit_sgro]].groupby(['TIPO_OPERACION'], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', crit_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', crit_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', crit_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD'], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
    else:
        base_filtro = base_filtro[['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', crit_sgro]].groupby(['TIPO_OPERACION', 'REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
        base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA'] == selected_ofic]

    base_filtro = base_filtro.sort_values(crit_sgro, ascending = False)
    base_filtro = base_filtro.reset_index()
    annotation = np.round((base_filtro[crit_sgro]*100/base_filtro[crit_sgro].sum()), decimals = 1, out = None)
    annotation = np.where(annotation >= 2.4, annotation.astype(str)+'%', '')

    color = {'ACTIVACION TDC': '#0B877D', 'APERTURAS PASIVO': '#126872', 'APROBACIONES CREDITOS': '#2D587B', 'DESEMBOLSOS CREDITOS': '#184169', 'OTRA': '#FFD351', 'PREAPROBADOS': '#121C25', 'SOLICITUDES': '#13314D', 'TRANSACCIONES CAJA': '#C9283E', 'TELEMERCADEO': 'rgb(69,117,180)'}

    data = []
    for i in base_filtro['TIPO_OPERACION']:
        data.append(
            Bar(
                y = 1,
                x = base_filtro[base_filtro['TIPO_OPERACION'] == i][crit_sgro],
                hoverinfo= 'text',
                marker = dict(color = color[i]),
                name = i,
                text =  base_filtro[base_filtro['TIPO_OPERACION'] == i][crit_sgro].astype(str) + ' inter.',
                orientation = 'h'
            )
        )

    annotations = []
    acumulado = 0

    for i in range(0,len(base_filtro)):
        annotations.append(
            dict(
                xref='x',
                yref='y',
                x = ((base_filtro[crit_sgro][i] / 2) + acumulado),
                y=0,
                text = annotation[i],
                font = dict(family='Helvetica', size=12, color='rgb(248, 248, 255)'),
                showarrow=False
                )
           )
        acumulado = acumulado + base_filtro[crit_sgro][i]

    layout = Layout(
        barmode = 'stack',
        title = '',
        xaxis = dict({'title':''}, showgrid=False, showticklabels = False),
        yaxis = dict({'title':''}, showgrid=False, showticklabels = False),
        margin = {'l': 40, 'b': 100, 't': 0, 'r': 30},
        showlegend = True,
#       paper_bgcolor = '#7f7f7f',
#       plot_bgcolor = '#c7c7c7',
        legend = dict(orientation = 'h')
        )

    layout['annotations'] = annotations

    return Figure(data = data, layout = layout)

#---------------------------------------------------------

#--------------------------- GRAPH 6 - TABLE TOP10 BEST

@app.callback(dash.dependencies.Output('graph-6', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_table(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    crit_sgro = 'crit_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA'], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
    else:
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]

    base_filtro['pen_sgro'] = np.round(base_filtro[selected_sgro]*100/base_filtro[crit_sgro], decimals = 1, out = None)
    base_filtro['txt_pen_sgro'] = base_filtro['pen_sgro'].astype(str)
    base_filtro['txt_pen_sgro'] = base_filtro['txt_pen_sgro'] + '%'

    base_filtro = base_filtro.sort_values('pen_sgro', ascending = False)
    base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA']!='OTRA']
    base_filtro = base_filtro.reset_index(drop=True)
    base_filtro = base_filtro.reset_index()
    base_filtro['index'] = base_filtro['index'] + 1
    base_filtro = base_filtro.sort_values('pen_sgro', ascending = False).head(10)
    base_filtro = base_filtro[['index', 'NOMBRE_OFICINA', 'CIUDAD', 'DEPARTAMENTO', selected_sgro, crit_sgro, 'txt_pen_sgro']]
    base_filtro.columns = ['Posición', 'Oficina', 'Ciudad', 'Departamento', 'Pólizas','Interacciones','Penetración']
    base_filtro

    base_filtro = ff.create_table(base_filtro)
    return base_filtro

#---------------------------------------------------------

#--------------------------- GRAPH 7 - TABLE TOP10 WORST

@app.callback(dash.dependencies.Output('graph-7', 'figure'),
    [dash.dependencies.Input('reg-drop', 'value'),
    dash.dependencies.Input('dpto-drop', 'value'),
    dash.dependencies.Input('ciud-drop', 'value'),
    dash.dependencies.Input('ofic-drop', 'value'),
    dash.dependencies.Input('sgro-drop', 'value'),
    dash.dependencies.Input('mes-range', 'value'),
    dash.dependencies.Input('inter-drop', 'value')])
def update_table(selected_reg, selected_dpto, selected_ciud, selected_ofic, selected_sgro, selected_mes, selected_inter):
    crit_sgro = 'crit_' + selected_sgro

    base_filtro = base[(base['numeroMES'] >= selected_mes[0])&(base['numeroMES'] <= selected_mes[1])]

    base_filtro = base_filtro[base_filtro['TIPO_OPERACION'].isin(selected_inter)]

    if selected_reg == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA'], as_index = False).sum()
    elif selected_dpto == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
    elif selected_ciud == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
    elif selected_ofic == 'TODAS':
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]
    else:
        base_filtro = base_filtro[['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA', selected_sgro, crit_sgro]].groupby(['REGIONAL', 'DEPARTAMENTO', 'CIUDAD', 'NOMBRE_OFICINA',], as_index = False).sum()
        base_filtro = base_filtro[base_filtro['REGIONAL'] == selected_reg]
        base_filtro = base_filtro[base_filtro['DEPARTAMENTO'] == selected_dpto]
        base_filtro = base_filtro[base_filtro['CIUDAD'] == selected_ciud]

    base_filtro['pen_sgro'] = np.round(base_filtro[selected_sgro]*100/base_filtro[crit_sgro], decimals = 1, out = None)
    base_filtro['txt_pen_sgro'] = base_filtro['pen_sgro'].astype(str)
    base_filtro['txt_pen_sgro'] = base_filtro['txt_pen_sgro'] + '%'

    base_filtro = base_filtro.sort_values('pen_sgro', ascending = False)
    base_filtro = base_filtro[base_filtro['NOMBRE_OFICINA']!='OTRA']
    base_filtro = base_filtro.reset_index(drop=True)
    base_filtro = base_filtro.reset_index()
    base_filtro['index'] = base_filtro['index'] + 1
    base_filtro = base_filtro.sort_values('pen_sgro', ascending = True).head(10)
    base_filtro = base_filtro[['index', 'NOMBRE_OFICINA', 'CIUDAD', 'DEPARTAMENTO', selected_sgro, crit_sgro, 'txt_pen_sgro']]
    base_filtro.columns = ['Posición', 'Oficina', 'Ciudad', 'Departamento', 'Pólizas','Interacciones','Penetración']
    base_filtro

    base_filtro = ff.create_table(base_filtro)
    return base_filtro

#---------------------------------------------------------



#--------------------------- CSS STYLING FILE - URL DELETES UNDO-REDO BUTTON

app.css.append_css({
   'external_url': (
       'https://rawgit.com/lwileczek/Dash/master/undo_redo5.css'
   )
})

#---------------------------------------------------------

#--------------------------- RUN APP

if __name__ == '__main__':
    app.run_server(debug = False, port = 8000)

#---------------------------------------------------------
