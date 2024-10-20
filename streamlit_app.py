import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Função para obter países da API do FMI
def get_countries():
    url = "https://www.imf.org/external/datamapper/api/v1/countries"
    response = requests.get(url)
    return response.json()["countries"]

# Função para obter indicadores da API do FMI
def get_indicators():
    url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    response = requests.get(url)
    return response.json()["indicators"]

# Função para obter dados da API do FMI
def get_data(country, indicator, start_year, end_year):
    url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator}/{country}/{start_year}/{end_year}"
    response = requests.get(url)
    return response.json()["values"][indicator][country]

# Carregar países e indicadores
countries = get_countries()
indicators = get_indicators()

# Criar dicionários para países e indicadores
country_options = {code: data["label"] for code, data in countries.items()}
indicator_options = {code: data["label"] for code, data in indicators.items()}

# Sidebar para seleção de países e indicadores
st.sidebar.header("Selecione os Parâmetros")
selected_countries = st.sidebar.multiselect(
    "Selecione Países:",
    options=list(country_options.keys()),
    format_func=lambda x: country_options[x]  # Formatação das opções
)

selected_indicators = st.sidebar.multiselect(
    "Selecione Indicadores:",
    options=list(indicator_options.keys()),
    format_func=lambda x: indicator_options[x]  # Formatação das opções
)

# Seleção de anos
start_year = st.sidebar.number_input("Ano de Início", min_value=2000, max_value=2024, value=2000)
end_year = st.sidebar.number_input("Ano de Fim", min_value=2000, max_value=2024, value=2024)

# Se pelo menos um país e um indicador foram selecionados
if selected_countries and selected_indicators:
    for country in selected_countries:
        for indicator in selected_indicators:
            try:
                # Tenta obter os dados
                data = get_data(country, indicator, start_year, end_year)
                
                # Formata os dados em um DataFrame
                df = pd.DataFrame(data.items(), columns=["Ano", "Valor"])
                df["Ano"] = df["Ano"].astype(int)

                # Gráfico
                fig = px.line(df, x="Ano", y="Valor", title=f"{indicator_options[indicator]} para {country_options[country]}")
                st.plotly_chart(fig)

                # Download de dados
                st.download_button(
                    label="Baixar Dados em CSV",
                    data=df.to_csv(index=False),
                    file_name=f"{country_options[country]}_{indicator_options[indicator]}.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Erro ao obter dados para {country_options[country]} e {indicator_options[indicator]}: {e}")
else:
    st.warning("Por favor, selecione pelo menos um país e um indicador.")
