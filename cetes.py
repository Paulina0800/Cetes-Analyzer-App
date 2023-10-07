#Librerias
import requests
import pandas as pd
import numpy as np
import datetime
from datetime import date
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

#Setup de la pagina
st.set_page_config(layout="wide")
st.title('Cetes')

st.header('Investment analysis')

col1, col2 =st.columns([1,2])

# Poner datos
with col1:
    st.subheader('Data:')
    start_date = str(st.date_input('**Start date:**', datetime.date(2010,1,1)))
    end_date = str(st.date_input('**End date:**'                                                                                                                                                                                                                                                             ))
    monto = float(st.number_input('Amount to invest:', value= 1000))
    retiro = float(st.number_input('How many days have passed since the purchase?', value= 7))

    
#Tocken de autenticción para acceder a la API de BANXICO:
token = '3a5cd44bc227e1953391c86ca0c59d4f54f09f32a64ea5fe699492ac2cfbd845'

#Función para descargar elementos de la página de BANXICO
def descarga_bmx_serie(serie,fechainicio,fechafin,token):
    url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/'+serie+'/datos/'+fechainicio+'/'+fechafin+''
    print(url)
    headers = {'Bmx-Token':token}
    response = requests.get(url,headers=headers)
    status = response.status_code
    if status != 200:
        return print('Error en la consulta, código {}'.format(status))
    else:
        raw_data = response.json()
        data = raw_data['bmx']['series'][0]['datos']
        df = pd.DataFrame(data)
        df['dato'] = df['dato'].apply(lambda x: float(x) if x != 'N/E' else 0)
        df['fecha'] = pd.to_datetime(df['fecha'], format = '%d/%m/%Y')
        df.set_index('fecha', inplace=True)
    return df

#Tasas de rendimiento de cetes
c = pd.DataFrame()
c['Cetes 28'] = descarga_bmx_serie('SF43936',start_date,end_date, token)
c['Cetes 91'] = descarga_bmx_serie('SF43939',start_date,end_date, token)
c['Cetes 182'] = descarga_bmx_serie('SF43942',start_date,end_date, token)
c['Cetes 364'] = descarga_bmx_serie('SF43945',start_date,end_date, token)
c['Cetes 728'] = descarga_bmx_serie('SF349785',start_date,end_date, token)
 
df = pd.DataFrame()

# creamos las columnas
df['Term'] = None
df['Yield rate (%)'] = None

# añadimos filas con los Terms y rendimiento por instrumento del último día solicitado con la api
df.loc['Cetes 28'] = [28, float(c['Cetes 28'].iloc[-1])]
df.loc['Cetes 91'] = [91, float(c['Cetes 91'].iloc[-1])]
df.loc['Cetes 182'] = [182, float(c['Cetes 182'].iloc[-1])]
df.loc['Cetes 364'] = [364, float(c['Cetes 364'].iloc[-1])]
df.loc['Cetes 728'] = [728, float(c['Cetes 728'].iloc[-1])]
df['Price'] = 10/( 1+ (df['Yield rate (%)']/100 * (df['Term'] /360)))
df['# Purchased Titles'] = np.trunc(monto/df['Price'])
df['$ Invested'] = df['# Purchased Titles']*df['Price']
df['Final Position'] = 10*df['# Purchased Titles']

#calculamos equivalencias
df['Equivalent Rate Cete 28 (%)'] = (((1+((df.iloc[0]['Yield rate (%)']/100)/360*28))**(df['Term']/28)-1)/df['Term'])*360*100
df['Equivalent Rate Cete 91 (%)'] = (((1+((df.iloc[1]['Yield rate (%)']/100)/360*91))**(df['Term']/91)-1)/df['Term'])*360*100
df['Equivalent Rate Cete 182 (%)'] = (((1+((df.iloc[2]['Yield rate (%)']/100)/360*182))**(df['Term']/182)-1)/df['Term'])*360*100
df['Equivalent Rate Cete 364 (%)'] = (((1+((df.iloc[3]['Yield rate (%)']/100)/360*364))**(df['Term']/364)-1)/df['Term'])*360*100
df['Equivalent Rate Cete 728 (%)'] = (((1+((df.iloc[4]['Yield rate (%)']/100)/360*728))**(df['Term']/728)-1)/df['Term'])*360*100

#ignoramos los correlacionados con sigo mismos
df.at['Cetes 28','Equivalent Rate Cete 28 (%)'] = '-'
df.at['Cetes 91','Equivalent Rate Cete 91 (%)'] = '-'
df.at['Cetes 182','Equivalent Rate Cete 182 (%)'] = '-'
df.at['Cetes 364','Equivalent Rate Cete 364 (%)'] = '-'
df.at['Cetes 728','Equivalent Rate Cete 728 (%)'] = '-'

#Calculamos por venta anticipada
df['Discount rate (%)'] = (((10-df['Price'])/10)/df['Term'])*360*100
df['Time Till Expiration'] = df['Term'] - retiro
df['New Price'] = 10 - (10*df['Discount rate (%)']/100*df['Time Till Expiration'])/360
df['New Yield rate (%)'] = (((df['New Price']/df['Price'])-1)/df['Time Till Expiration'])*360*100
df['Revenue'] = (df['New Price']-df['Price'])*df['# Purchased Titles']

#Seccion de graficas historicas
with col2: 
    st.subheader('Historical graph(s):')
    term = st.multiselect(
         "Select the instrument to analyze:", 
         options = list(df['Term'].unique()),
         format_func = lambda x: "Cete " + str(int(x)),
         default = df['Term'][0])
    
    fig = go.Figure()

    if 28.0 in term:
        fig.add_trace(go.Scatter(
        x=c.index,
        y=c['Cetes 28'],
        name='Cete 28',
        mode='lines'))

    if 91.0 in term:
        fig.add_trace(go.Scatter(
        x=c.index,
        y=c['Cetes 91'],
        name='Cete 91',
        mode='lines'))
    
    if 182.0 in term:
        fig.add_trace(go.Scatter(
        x=c.index,
        y=c['Cetes 182'],
        name='Cete 182',
        mode='lines'))
    
    if 364.0 in term:
        fig.add_trace(go.Scatter(
        x=c.index,
        y=c['Cetes 364'],
        name='Cete 364',
        mode='lines'))
    
    if 728.0 in term:
        fig.add_trace(go.Scatter(
        x=c.index,
        y=c['Cetes 728'],
        name='Cete 728',
        mode='lines'))
     
    st.plotly_chart(fig) 

#Resultados de calculos en streamlit
st.subheader('Comparative Dataframe')
df = df.query("Term == @term")
basic = df.iloc[:,[0,1,2,3,4,5]]
eq = df.iloc[:,[6,7,8,9,10]]
anti = df.iloc[:,[11,12,13,14,15]]

st.dataframe(basic) 

st.subheader('Equivalent Rates:')
st.dataframe(eq)

st.subheader('Pre-sale:')
st.dataframe(anti)









