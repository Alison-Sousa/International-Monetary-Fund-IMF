import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(
    page_title='FMI Dashboard',
    page_icon=':earth_americas:',
)

# Função para obter todos os países
@st.cache_data
def get_countries():
    """Obter lista de países do FMI."""
    try:
        url = "https://www.imf.org/external/datamapper/api/v1/countries"
        response = requests.get(url)
        countries = response.json()
        
        if 'countries' in countries:
            # Transformando os dados em DataFrame
            country_data = [{'id': code, 'name': info['label']} for code, info in countries['countries'].items()]
            return pd.DataFrame(country_data)
        else:
            st.error("Não foram encontrados países. Verifique a resposta da API.")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Erro ao obter países: {e}")
        return pd.DataFrame()

# Função para obter todos os indicadores
@st.cache_data
def get_indicators():
    """Obter lista de indicadores do FMI."""
    try:
        url = "https://www.imf.org/external/datamapper/api/v1/indicators"
        response = requests.get(url)
        indicators = response.json()
        
        if 'indicators' in indicators:
            # Transformando os dados em DataFrame
            indicator_data = [{'id': code, 'name': info['label'], 'description': info.get('description', '')} for code, info in indicators['indicators'].items()]
            return pd.DataFrame(indicator_data)
        else:
            st.error("Não foram encontrados indicadores. Verifique a resposta da API.")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Erro ao obter indicadores: {e}")
        return pd.DataFrame()

# Função para obter dados do FMI
@st.cache_data
def get_indicator_data(country_id, indicator_id, start_year, end_year):
    """Obter dados de um indicador específico para um país do FMI."""
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
        response = requests.get(url)
        data = response.json()

        if not data or 'data' not in data:
            st.error("Não foram encontrados dados para o país e indicador selecionados.")
            return pd.DataFrame()

        df = pd.DataFrame(data['data'])
        df.rename(columns={'year': 'year', 'value': 'value'}, inplace=True)
        return df[['year', 'value']]
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
    try:
        # Verificando se as colunas existem
        if 'id' in countries.columns and 'name' in countries.columns:
            country_options = countries.set_index('id')['name'].to_dict()
            selected_country = st.sidebar.selectbox(
                'Escolha um país',
                list(country_options.keys()),
                format_func=lambda x: country_options[x]
            )
        else:
            st.error("Colunas 'id' e 'name' não encontradas na resposta dos países.")
            st.stop()

    except Exception as e:
        st.error(f"Erro ao processar países: {e}")
        st.stop()

if indicators.empty:
    st.warning("Nenhum indicador disponível.")
else:
    try:
        # Verificando se as colunas existem
        if 'id' in indicators.columns and 'name' in indicators.columns:
            indicator_options = indicators.set_index('id')['name'].to_dict()
            selected_indicator = st.sidebar.selectbox(
                'Escolha um indicador',
                list(indicator_options.keys()),
                format_func=lambda x: indicator_options[x]
            )

            # Definindo o intervalo de anos
            min_year = 2000
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
        else:
            st.error("Colunas 'id' e 'name' não encontradas na resposta dos indicadores.")
            st.stop()

    except Exception as e:
        st.error(f"Erro ao processar indicadores: {e}")
