import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(
    page_title='World Bank Dashboard',
    page_icon=':earth_americas:',
)

# Função para obter todos os países
@st.cache_data
def get_countries():
    """Obter lista de países do Banco Mundial."""
    try:
        url = "https://api.worldbank.org/v2/country?format=json"
        response = requests.get(url)
        data = response.json()
        
        if len(data) < 2:
            st.error("Não foram encontrados países.")
            return pd.DataFrame()

        countries = data[1]  # A segunda parte da resposta contém os dados

        country_list = []
        for country in countries:
            country_list.append({
                'id': country['id'],
                'name': country['name'],
            })

        return pd.DataFrame(country_list)
    except Exception as e:
        st.error(f"Erro ao obter países: {e}")
        return pd.DataFrame()

# Função para obter todos os indicadores
@st.cache_data
def get_indicators():
    """Obter lista de indicadores do Banco Mundial."""
    try:
        url = "https://api.worldbank.org/v2/indicator?format=json"
        response = requests.get(url)
        data = response.json()

        if len(data) < 2:
            st.error("Não foram encontrados indicadores.")
            return pd.DataFrame()

        indicators = data[1]  # A segunda parte da resposta contém os dados

        indicator_list = []
        for indicator in indicators:
            indicator_list.append({
                'id': indicator['id'],
                'name': indicator['name'],
            })

        return pd.DataFrame(indicator_list)
    except Exception as e:
        st.error(f"Erro ao obter indicadores: {e}")
        return pd.DataFrame()

# Função para obter dados do Banco Mundial
@st.cache_data
def get_indicator_data(country_id, indicator_id, start_year, end_year):
    """Obter dados de um indicador específico para um país do Banco Mundial."""
    try:
        url = f"https://api.worldbank.org/v2/country/{country_id}/indicator/{indicator_id}?date={start_year}:{end_year}&format=json"
        response = requests.get(url)
        data = response.json()
        
        if len(data) < 2:
            st.error("Não foram encontrados dados para o país e indicador selecionados.")
            return pd.DataFrame()

        df = pd.DataFrame(data[1])  # A segunda parte da resposta contém os dados
        df['indicator'] = df['indicator'].apply(lambda x: x['value'])  # Extrair o nome do indicador
        df['country'] = df['country'].apply(lambda x: x['value'])      # Extrair o nome do país
        df.rename(columns={'date': 'year', 'value': 'value'}, inplace=True)
        return df[['indicator', 'country', 'year', 'value']]
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return pd.DataFrame()

# Sidebar para seleção de país e indicador
st.sidebar.header('Filtrar por País e Indicador')
countries = get_countries()
indicators = get_indicators()

if countries.empty:
    st.warning("Nenhum país disponível.")
else:
    country_options = countries.set_index('id')['name'].to_dict()
    selected_country = st.sidebar.selectbox(
        'Escolha um país',
        list(country_options.keys()),
        format_func=lambda x: country_options[x]
    )

if indicators.empty:
    st.warning("Nenhum indicador disponível.")
else:
    indicator_options = indicators.set_index('id')['name'].to_dict()
    selected_indicator = st.sidebar.selectbox(
        'Escolha um indicador',
        list(indicator_options.keys()),
        format_func=lambda x: indicator_options[x]
    )

    # Definindo o intervalo de anos
    min_year = 1960
    max_year = 2022
    from_year, to_year = st.sidebar.slider(
        'Selecione o intervalo de anos',
        min_value=min_year,
        max_value=max_year,
        value=[min_year, max_year]
    )

    # Obtendo os dados do indicador selecionado para o país selecionado
    data_df = get_indicator_data(selected_country, selected_indicator, from_year, to_year)

    # Verificando se o DataFrame não está vazio
    if not data_df.empty:
        st.header(f'Dados de {indicator_options[selected_indicator]} para {country_options[selected_country]} ao longo do tempo')
        data_df['year'] = pd.to_datetime(data_df['year'], format='%Y')
        st.line_chart(data_df.set_index('year')['value'])
    else:
        st.warning("Nenhum dado disponível para o país e indicador selecionados.")
