import streamlit as st
import pandas as pd
import requests
import json

# Configuração da página
st.set_page_config(
    page_title='World Bank Dashboard',
    page_icon=':earth_americas:',
)

# Função para obter todos os indicadores
@st.cache_data
def get_all_indicators():
    """Obter todos os indicadores do Banco Mundial."""
    try:
        url = "https://api.worldbank.org/v2/indicator?format=json"
        response = requests.get(url)
        indicators = response.json()[1]  # A segunda parte da resposta contém os dados
        return pd.DataFrame(indicators)[['id', 'name']]
    except Exception as e:
        st.error(f"Erro ao obter indicadores: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# Função para obter dados do Banco Mundial
@st.cache_data
def get_indicator_data(indicator, start_year, end_year):
    """Obter dados de um indicador específico do Banco Mundial."""
    try:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?date={start_year}:{end_year}&format=json"
        response = requests.get(url)
        data = response.json()[1]  # A segunda parte da resposta contém os dados
        # Criar DataFrame e processar colunas
        df = pd.DataFrame(data)
        # Processar as colunas de interesse
        df['indicator'] = df['indicator'].apply(lambda x: json.loads(x)['value'])
        df['country'] = df['country'].apply(lambda x: json.loads(x)['value'])
        df.rename(columns={'date': 'year', 'value': 'poverty_headcount'}, inplace=True)
        return df[['indicator', 'country', 'year', 'poverty_headcount']]
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# Sidebar para seleção de indicadores
st.sidebar.header('Select Indicator')
indicators = get_all_indicators()

if indicators.empty:
    st.warning("No indicators available.")
else:
    indicator_options = indicators.set_index('id')['name'].to_dict()

    selected_indicator = st.sidebar.selectbox(
        'Choose an indicator',
        list(indicator_options.keys()),
        format_func=lambda x: indicator_options[x]  # Para mostrar o nome do indicador
    )

    # Definindo o intervalo de anos
    min_year = 1960
    max_year = 2022
    from_year, to_year = st.sidebar.slider(
        'Select the year range',
        min_value=min_year,
        max_value=max_year,
        value=[min_year, max_year]
    )

    # Obtendo os dados do indicador selecionado
    data_df = get_indicator_data(selected_indicator, from_year, to_year)

    # Verificando se o DataFrame não está vazio
    if not data_df.empty:
        # Exibindo a estrutura dos dados para depuração
        st.write("DataFrame structure:")
        st.write(data_df)

        # Verificando se as colunas necessárias estão presentes
        if 'country' in data_df.columns and 'year' in data_df.columns and 'poverty_headcount' in data_df.columns:
            # Filtrando os dados
            st.header(f'{indicator_options[selected_indicator]} Over Time')
            data_df['year'] = pd.to_datetime(data_df['year'], format='%Y')
            st.line_chart(data_df.set_index('year')['poverty_headcount'])

            # Mostrando dados de alguns países
            st.header(f'{indicator_options[selected_indicator]} in Selected Countries')
            countries = data_df['country'].unique()
            selected_countries = st.multiselect(
                'Choose countries to display',
                countries
            )

            # Filtrando os dados para os países selecionados
            if selected_countries:
                filtered_data = data_df[data_df['country'].isin(selected_countries)]
                for country in selected_countries:
                    country_data = filtered_data[filtered_data['country'] == country]
                    st.line_chart(country_data.set_index('year')['poverty_headcount'])
            else:
                st.warning("Select at least one country to view data.")
        else:
            st.warning("Missing expected columns in the data.")
    else:
        st.warning("No data available for the selected indicator and year range.")
