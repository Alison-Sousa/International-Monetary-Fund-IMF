import streamlit as st
import requests
import pandas as pd
import altair as alt

# Função para obter a lista de países
def get_countries():
    url = "https://www.imf.org/external/datamapper/api/v1/countries"
    response = requests.get(url)
    data = response.json()
    countries = {item['id']: item['name'] for item in data['countries']}
    return countries

# Função para obter a lista de indicadores
def get_indicators():
    url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    response = requests.get(url)
    data = response.json()
    indicators = {item['id']: item['name'] for item in data['indicators']}
    return indicators

# Função para obter dados do indicador para um país específico
def get_indicator_data(country, indicator):
    url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator}/{country}"
    response = requests.get(url)
    data = response.json()
    return data

# Configuração do Streamlit
st.title("API do FMI - Dados de Países e Indicadores")

# Sidebar
st.sidebar.header("Configurações")
countries = get_countries()
indicators = get_indicators()

# Seleção de país e indicador
selected_country = st.sidebar.selectbox("Selecione um País", options=list(countries.keys()), format_func=lambda x: countries[x])
selected_indicator = st.sidebar.selectbox("Selecione um Indicador", options=list(indicators.keys()), format_func=lambda x: indicators[x])

# Botão para buscar dados
if st.sidebar.button("Buscar Dados"):
    data = get_indicator_data(selected_country, selected_indicator)

    # Processar os dados para o gráfico
    df = pd.DataFrame(data['data'])
    df.columns = ['Year', 'Value']
    df['Year'] = pd.to_datetime(df['Year'], format='%Y')

    # Criar gráfico interativo
    chart = alt.Chart(df).mark_line().encode(
        x='Year:T',
        y='Value:Q'
    ).properties(
        title=f"{indicators[selected_indicator]} para {countries[selected_country]}"
    )

    st.altair_chart(chart, use_container_width=True)
