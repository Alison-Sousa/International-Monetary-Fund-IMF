import streamlit as st
import requests
import pandas as pd

# Título do aplicativo
st.title("Dashboard de Indicadores Econômicos do FMI")

# Função para obter a lista de países
@st.cache_data
def get_countries():
    """Obter lista de países do FMI."""
    url = "https://www.imf.org/external/datamapper/api/v1/countries"
    response = requests.get(url)
    data = response.json()
    countries = {key: value['label'] for key, value in data['countries'].items()}
    return countries

# Função para obter a lista de indicadores
@st.cache_data
def get_indicators():
    """Obter lista de indicadores do FMI."""
    url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    response = requests.get(url)
    data = response.json()
    indicators = {key: value['label'] for key, value in data['indicators'].items()}
    return indicators

# Função para obter dados do FMI com depuração
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

# Sidebar para seleção
with st.sidebar:
    st.header("Configurações")
    
    countries = get_countries()
    country_id = st.selectbox("Selecione um País:", options=list(countries.keys()), format_func=lambda x: countries[x])
    
    indicators = get_indicators()
    indicator_id = st.selectbox("Selecione um Indicador:", options=list(indicators.keys()), format_func=lambda x: indicators[x])
    
    start_year = st.number_input("Ano de Início:", value=2000, min_value=1900, max_value=2024)
    end_year = st.number_input("Ano de Fim:", value=2024, min_value=1900, max_value=2024)

    # Botão para obter dados
    if st.button("Obter Dados"):
        df = get_indicator_data(country_id, indicator_id, start_year, end_year)
        if not df.empty:
            st.session_state.df = df  # Armazena os dados em session_state para uso posterior
            st.success("Dados obtidos com sucesso!")
        else:
            st.warning("Nenhum dado disponível para o intervalo de anos selecionado.")

# Exibição de gráficos e download
if 'df' in st.session_state:
    st.subheader(f"Gráfico para {countries[country_id]} - {indicators[indicator_id]}")
    st.line_chart(st.session_state.df.set_index('year'))
    
    # Download de dados
    st.download_button(
        label="Baixar Dados em CSV",
        data=st.session_state.df.to_csv(index=False),
        file_name="indicadores_economicos.csv",
        mime="text/csv"
    )
