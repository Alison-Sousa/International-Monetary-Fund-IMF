import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

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
def get_indicator_data(country_ids, indicator_id, start_year, end_year):
    """Obter dados de um indicador específico para um ou mais países do FMI."""
    url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{'/'.join(country_ids)}/{start_year}/{end_year}"
    response = requests.get(url)
    data = response.json()

    if 'values' not in data or not data['values']:
        st.error("Não foram encontrados dados para os países e indicadores selecionados.")
        return pd.DataFrame()

    records = []
    for country in country_ids:
        country_data = data['values'][indicator_id].get(country, {})
        for year, value in country_data.items():
            records.append({'year': year, 'country': countries[country], 'value': value})

    df = pd.DataFrame(records)
    return df

# Função para criar gráficos
def plot_graph(df):
    """Plotar gráfico com os dados fornecidos."""
    fig = go.Figure()
    for country in df['country'].unique():
        country_data = df[df['country'] == country]
        fig.add_trace(go.Scatter(x=country_data['year'], y=country_data['value'],
                                 mode='lines+markers', name=country))

    fig.update_layout(title='Indicador Econômico ao Longo do Tempo',
                      xaxis_title='Ano',
                      yaxis_title='Valor',
                      legend_title='Países')
    
    st.plotly_chart(fig)

# Função para download dos dados
def download_csv(df):
    """Gerar link para download dos dados em CSV."""
    csv = df.to_csv(index=False)
    st.download_button("Baixar dados como CSV", csv, "dados_economicos.csv", "text/csv")

# Seleção de países
countries = get_countries()
country_ids = st.sidebar.multiselect("Selecione Países:", options=list(countries.keys()), format_func=lambda x: countries[x])

# Seleção de indicadores
indicators = get_indicators()
indicator_id = st.sidebar.selectbox("Selecione um Indicador:", options=list(indicators.keys()), format_func=lambda x: indicators[x])

# Seleção de anos
start_year = st.sidebar.number_input("Ano de Início:", value=2000, min_value=1900, max_value=2024)
end_year = st.sidebar.number_input("Ano de Fim:", value=2024, min_value=1900, max_value=2024)

# Botão para obter dados
if st.sidebar.button("Obter Dados"):
    if not country_ids:
        st.error("Por favor, selecione pelo menos um país.")
    else:
        df = get_indicator_data(country_ids, indicator_id, start_year, end_year)
        if not df.empty:
            st.write("Dados Obtidos:")
            st.dataframe(df)
            plot_graph(df)
            download_csv(df)
        else:
            st.warning("Nenhum dado disponível para o intervalo de anos selecionado.")
