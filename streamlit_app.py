import streamlit as st
import pandas as pd
import wbgapi as wb
import math

# Configuração da página
st.set_page_config(
    page_title='World Bank Dashboard',
    page_icon=':earth_americas:',
)

# Função para obter dados do Banco Mundial
@st.cache_data
def get_indicator_data(indicator, start_year, end_year):
    """Obter dados de um indicador específico do Banco Mundial."""
    data = wb.data.get_dataframe(indicator, mdb=True, time=(start_year, end_year))
    data.reset_index(inplace=True)
    return data

# Sidebar para seleção de indicadores
st.sidebar.header('Select Indicator Category')
indicator_category = st.sidebar.selectbox(
    'Choose a category',
    ['Economic Indicators', 'Social Indicators', 'Political Indicators']
)

indicators = {
    'Economic Indicators': {
        'GDP (current US$)': 'NY.GDP.MKTP.CD',
        'Exchange Rate (LCU per US$, period average)': 'PA.NUS.FCRF',
        # Adicione mais indicadores econômicos aqui
    },
    'Social Indicators': {
        'Poverty Headcount Ratio at $1.90 a Day': 'SI.POV.DDAY',
        'Literacy Rate': 'SE.ADT.LITR.ZS',
        # Adicione mais indicadores sociais aqui
    },
    'Political Indicators': {
        'Government Effectiveness': 'NY.GDP.PCAP.CD',
        'Voice and Accountability': 'NY.GDP.MKTP.CD',
        # Adicione mais indicadores políticos aqui
    },
}

selected_indicator = st.sidebar.selectbox(
    'Select an indicator',
    list(indicators[indicator_category].keys())
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
indicator_code = indicators[indicator_category][selected_indicator]
data_df = get_indicator_data(indicator_code, from_year, to_year)

# Filtrando os dados
st.header(f'{selected_indicator} Over Time')
st.line_chart(data_df.set_index('year'))

# Mostrando dados de alguns países
st.header(f'{selected_indicator} in Selected Countries')
selected_countries = st.multiselect(
    'Choose countries to display',
    data_df['country'].unique()
)

# Filtrando os dados para os países selecionados
if selected_countries:
    filtered_data = data_df[data_df['country'].isin(selected_countries)]
    for country in selected_countries:
        country_data = filtered_data[filtered_data['country'] == country]
        st.line_chart(country_data.set_index('year'))
else:
    st.warning("Select at least one country to view data.")
