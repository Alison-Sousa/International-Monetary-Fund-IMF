import streamlit as st
import requests
import pandas as pd
import plotly.express as px

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

        # Verifica se os dados estão presentes
        if "values" in data and indicator_id in data["values"] and country_id in data["values"][indicator_id]:
            years_data = data["values"][indicator_id][country_id]
            # Converte os dados em DataFrame
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

# Permitir múltiplos países com um campo de texto
country_input = st.sidebar.text_input("Digite os Nomes dos Países (separados por vírgula):")
country_ids = []

# Processa a entrada para obter os country_ids correspondentes
if country_input:
    country_names = [name.strip() for name in country_input.split(',')]
    for name in country_names:
        for key, value in countries.items():
            if value.lower() == name.lower():
                country_ids.append(key)

indicators = get_indicators()
indicator_id = st.sidebar.selectbox("Selecione um Indicador:", options=list(indicators.keys()), format_func=lambda x: indicators[x])

start_year = st.sidebar.number_input("Ano de Início:", value=2000, min_value=1900, max_value=2024)
end_year = st.sidebar.number_input("Ano de Fim:", value=2024, min_value=1900, max_value=2024)

# Obter dados para os países inseridos
if country_ids:
    all_data = pd.DataFrame()
    for country_id in country_ids:
        df = get_indicator_data(country_id, indicator_id, start_year, end_year)
        all_data = pd.concat([all_data, df], ignore_index=True)

    if not all_data.empty:
        # Filtra os dados conforme o intervalo de anos selecionado
        all_data_filtered = all_data[(all_data['year'] >= start_year) & (all_data['year'] <= end_year)]
        if not all_data_filtered.empty:
            # Plota o gráfico interativo
            fig = px.line(all_data_filtered, x='year', y='value', color='country_id', 
                          title=f"{indicators[indicator_id]} para os países selecionados",
                          labels={'value': indicators[indicator_id], 'year': 'Ano'},
                          markers=True)
            fig.update_traces(line=dict(width=2), marker=dict(size=5))
            fig.update_layout(hovermode='x unified', showlegend=True)
            st.plotly_chart(fig)

            # Exibe a URL abaixo do gráfico
            for country_id in country_ids:
                url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
                st.markdown(f"**Dados disponíveis em:** [API URL para {countries[country_id]}]({url})")

            # Botão para download do CSV
            csv = all_data_filtered.to_csv(index=False)
            st.download_button(
                label="Baixar dados como CSV",
                data=csv,
                file_name="dados_indicadores.csv",
                mime="text/csv",
            )
        else:
            st.warning("Nenhum dado disponível para o intervalo de anos selecionado.")
    else:
        st.warning("Não foi possível obter dados para os países selecionados.")
else:
    st.warning("Por favor, digite um ou mais nomes de países válidos.")
