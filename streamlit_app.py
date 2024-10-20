import streamlit as st
import requests
import pandas as pd

# Título do aplicativo
st.title("Dashboard de Indicadores Econômicos do FMI")

# Função para obter a lista de países
@st.cache_data
def get_countries():
    """Obter lista de países do FMI."""
    try:
        url = "https://www.imf.org/external/datamapper/api/v1/countries"
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        data = response.json()
        countries = {key: value['label'] for key, value in data['countries'].items()}
        return countries
    except requests.RequestException:
        st.error("Erro ao carregar a lista de países. Tente novamente mais tarde.")
        return {}
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os países: {e}")
        return {}

# Função para obter a lista de indicadores
@st.cache_data
def get_indicators():
    """Obter lista de indicadores do FMI."""
    try:
        url = "https://www.imf.org/external/datamapper/api/v1/indicators"
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        data = response.json()
        indicators = {key: value['label'] for key, value in data['indicators'].items()}
        return indicators
    except requests.RequestException:
        st.error("Erro ao carregar a lista de indicadores. Tente novamente mais tarde.")
        return {}
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os indicadores: {e}")
        return {}

# Função para obter dados do FMI com depuração
@st.cache_data
def get_indicator_data(country_id, indicator_id, start_year, end_year):
    """Obter dados de um indicador específico para um país do FMI."""
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro se a requisição falhar
        data = response.json()

        if not data or 'data' not in data:
            return pd.DataFrame()  # Retorna DataFrame vazio se não houver dados

        df = pd.DataFrame(data['data'])
        df.rename(columns={'year': 'year', 'value': 'value'}, inplace=True)
        return df[['year', 'value']]
    except requests.RequestException:
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro na requisição
    except Exception as e:
        st.error(f"Ocorreu um erro ao obter os dados: {e}")
        return pd.DataFrame()

# Sidebar para seleção
with st.sidebar:
    countries = get_countries()
    if countries:
        selected_countries = st.multiselect("Selecione Países:", options=list(countries.keys()), format_func=lambda x: countries[x])
    else:
        selected_countries = []  # Define uma lista vazia se não houver países

    indicators = get_indicators()
    if indicators:
        selected_indicators = st.multiselect("Selecione Indicadores:", options=list(indicators.keys()), format_func=lambda x: indicators[x])
    else:
        selected_indicators = []  # Define uma lista vazia se não houver indicadores

    start_year = st.number_input("Ano de Início:", value=2000, min_value=1900, max_value=2024)
    end_year = st.number_input("Ano de Fim:", value=2024, min_value=1900, max_value=2024)

# Botão para obter dados
if st.button("Obter Dados"):
    if not selected_countries or not selected_indicators:
        st.warning("Por favor, selecione pelo menos um país e um indicador.")
    else:
        all_data = []
        
        # Obtém dados para cada país e indicador selecionados
        for country_id in selected_countries:
            for indicator_id in selected_indicators:
                df = get_indicator_data(country_id, indicator_id, start_year, end_year)
                if not df.empty:
                    df['country'] = countries[country_id]  # Adiciona nome do país
                    df['indicator'] = indicators[indicator_id]  # Adiciona nome do indicador
                    all_data.append(df)

        if all_data:
            combined_df = pd.concat(all_data)
            
            # Exibe os dados em uma tabela
            st.write("Dados Obtidos:")
            st.dataframe(combined_df)

            # Gráfico
            st.line_chart(combined_df.set_index('year')['value'])

            # Download de dados
            st.download_button(
                label="Baixar Dados em CSV",
                data=combined_df.to_csv(index=False),
                file_name="indicadores_economicos.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhum dado disponível para o intervalo de anos selecionado.")
