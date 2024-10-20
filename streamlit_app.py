import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(
    page_title='World Bank Dashboard',
    page_icon=':earth_americas:',
)

# Função para obter todos os indicadores econômicos
@st.cache_data
def get_economic_indicators():
    """Obter indicadores econômicos do Banco Mundial."""
    try:
        url = "https://api.worldbank.org/v2/document?format=json"
        response = requests.get(url)
        data = response.json()

        # Verifica se a resposta contém dados
        if len(data) < 2:
            st.error("Não foram encontrados indicadores.")
            return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

        documents = data[1]  # A segunda parte da resposta contém os dados

        # Criar uma lista para armazenar os indicadores
        indicator_list = []

        # Extrair os dados dos documentos
        for doc_id, doc_info in documents.items():
            indicator_list.append({
                'id': doc_info['id'],
                'name': doc_info['display_title'],
            })

        return pd.DataFrame(indicator_list)
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
        data = response.json()
        
        # Verifica se a resposta contém dados
        if len(data) < 2:
            st.error("Não foram encontrados dados para o indicador selecionado.")
            return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados

        df = pd.DataFrame(data[1])  # A segunda parte da resposta contém os dados
        # Processar as colunas de interesse
        df['indicator'] = df['indicator'].apply(lambda x: x['value'])  # Extrair o nome do indicador
        df['country'] = df['country'].apply(lambda x: x['value'])      # Extrair o nome do país
        df.rename(columns={'date': 'year', 'value': 'poverty_headcount'}, inplace=True)
        return df[['indicator', 'country', 'year', 'poverty_headcount']]
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

# Sidebar para seleção de indicadores
st.sidebar.header('Select Economic Indicator')
indicators = get_economic_indicators()

if indicators.empty:
    st.warning("Nenhum indicador disponível.")
else:
    indicator_options = indicators.set_index('id')['name'].to_dict()

    selected_indicator = st.sidebar.selectbox(
        'Escolha um indicador',
        list(indicator_options.keys()),
        format_func=lambda x: indicator_options[x]  # Para mostrar o nome do indicador
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

    # Obtendo os dados do indicador selecionado
    data_df = get_indicator_data(selected_indicator, from_year, to_year)

    # Verificando se o DataFrame não está vazio
    if not data_df.empty:
        st.header(f'{indicator_options[selected_indicator]} ao longo do tempo')
        data_df['year'] = pd.to_datetime(data_df['year'], format='%Y')
        st.line_chart(data_df.set_index('year')['poverty_headcount'])

        # Mostrando dados de alguns países
        st.header(f'{indicator_options[selected_indicator]} em Países Selecionados')
        countries = data_df['country'].unique()
        selected_countries = st.multiselect(
            'Escolha os países para exibir',
            countries
        )

        # Filtrando os dados para os países selecionados
        if selected_countries:
            filtered_data = data_df[data_df['country'].isin(selected_countries)]
            for country in selected_countries:
                country_data = filtered_data[filtered_data['country'] == country]
                st.line_chart(country_data.set_index('year')['poverty_headcount'])
        else:
            st.warning("Selecione pelo menos um país para visualizar os dados.")
    else:
        st.warning("Nenhum dado disponível para o indicador e intervalo de anos selecionados.")
