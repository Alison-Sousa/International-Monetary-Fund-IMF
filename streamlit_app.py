import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

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

# Função para obter dados do FMI
@st.cache_data
def get_indicator_data(country_id, indicator_id, start_year, end_year):
    """Obter dados de um indicador específico para um país do FMI."""
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
        response = requests.get(url)
        data = response.json()

        if "values" in data and indicator_id in data["values"] and country_id in data["values"][indicator_id]:
            years_data = data["values"][indicator_id][country_id]
            df = pd.DataFrame(years_data.items(), columns=['year', 'value'])
            df['year'] = pd.to_numeric(df['year'])
            return df
        else:
            return pd.DataFrame()  # Retorna um DataFrame vazio se não houver dados
    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")
        return pd.DataFrame()

# Sidebar para seleção de países, indicadores e anos
st.sidebar.header("Configurações de Pesquisa")
countries = get_countries()
country_id = st.sidebar.selectbox("Selecione um País:", options=list(countries.keys()), format_func=lambda x: countries[x])
indicators = get_indicators()
indicator_id = st.sidebar.selectbox("Selecione um Indicador:", options=list(indicators.keys()), format_func=lambda x: indicators[x])
start_year = st.sidebar.number_input("Ano de Início:", value=2000, min_value=1900, max_value=2024)
end_year = st.sidebar.number_input("Ano de Fim:", value=2024, min_value=1900, max_value=2024)

# Obter dados automaticamente ao mudar as seleções
df = get_indicator_data(country_id, indicator_id, start_year, end_year)
if not df.empty:
    df_filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    if not df_filtered.empty:
        fig = px.line(df_filtered, x='year', y='value', title=f"{indicators[indicator_id]} de {countries[country_id]}",
                      markers=True, line_shape='linear', template='plotly_dark')
        
        color_map = px.colors.qualitative.Plotly
        fig.update_traces(line=dict(color=color_map[np.random.randint(0, len(color_map))], width=3))
                          )
        fig.update_layout(xaxis_title='Ano', yaxis_title='Valor', title_x=0.5)

        st.plotly_chart(fig)

        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
        st.markdown(f"**Dados disponíveis em:** [API URL]({url})")

        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Baixar dados como CSV",
            data=csv,
            file_name=f"{countries[country_id]}_{indicators[indicator_id]}.csv",
            mime="text/csv",
        )
    else:
        st.warning("Nenhum dado disponível para o intervalo de anos selecionado.")
