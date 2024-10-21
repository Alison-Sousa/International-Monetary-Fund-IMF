import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Title of the application
st.title("IMF Economic Indicators Dashboard")

# Add the logo.svg image in the sidebar
st.sidebar.image("logo.svg", use_column_width=True)

# Function to get the list of countries
@st.cache_data
def get_countries():
    """Get the list of countries from the IMF."""
    url = "https://www.imf.org/external/datamapper/api/v1/countries"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch countries: {response.status_code} - {response.text}")
        return {}
    
    try:
        data = response.json()
        countries = {key: value['label'] for key, value in data['countries'].items()}
        return countries
    except ValueError as e:
        st.error(f"Error parsing JSON response for countries: {e}")
        return {}

# Function to get the list of indicators
@st.cache_data
def get_indicators():
    """Get the list of indicators from the IMF."""
    url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch indicators: {response.status_code} - {response.text}")
        return {}
    
    try:
        data = response.json()
        indicators = {key: value['label'] for key, value in data['indicators'].items()}
        return indicators
    except ValueError as e:
        st.error(f"Error parsing JSON response for indicators: {e}")
        return {}

# Function to get data from the IMF
@st.cache_data
def get_indicator_data(country_id, indicator_id):
    """Get data for a specific indicator for a country from the IMF."""
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}"
        response = requests.get(url)
        
        if response.status_code != 200:
            st.error(f"Error while fetching data: {response.status_code} - {response.text}")
            return pd.DataFrame()
        
        if not response.text:
            st.error("Error: Received empty response.")
            return pd.DataFrame()
        
        try:
            data = response.json()
        except ValueError as e:
            st.error(f"Error: Unable to parse JSON response. {e} - Response content: {response.text}")
            return pd.DataFrame()

        # Check if the data is present
        if "values" in data and indicator_id in data["values"] and country_id in data["values"][indicator_id]:
            years_data = data["values"][indicator_id][country_id]
            # Convert the data into a DataFrame
            df = pd.DataFrame(years_data.items(), columns=['year', 'value'])
            df['year'] = pd.to_numeric(df['year'])
            return df
        else:
            st.error("Error: No data available for the selected country and indicator.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error while obtaining data: {e}")
        return pd.DataFrame()

# Sidebar for selecting countries and indicators
st.sidebar.header("Search Settings")
countries = get_countries()
country_id = st.sidebar.selectbox("Select a Country:", options=list(countries.keys()), format_func=lambda x: countries[x])

indicators = get_indicators()
indicator_id = st.sidebar.selectbox("Select an Indicator:", options=list(indicators.keys()), format_func=lambda x: indicators[x])

# Automatically obtain data upon changing selections
df = get_indicator_data(country_id, indicator_id)

if not df.empty:
    # Select start and end year based on available data
    start_year = df['year'].min()
    end_year = df['year'].max()

    selected_start_year = st.sidebar.number_input("Start Year:", value=start_year, min_value=start_year, max_value=end_year)
    selected_end_year = st.sidebar.number_input("End Year:", value=end_year, min_value=start_year, max_value=end_year)

    # Filter the data according to the selected year range
    df_filtered = df[(df['year'] >= selected_start_year) & (df['year'] <= selected_end_year)]
    
    if not df_filtered.empty:
        # Plot the interactive graph
        fig = px.line(df_filtered, x='year', y='value', 
                      title=f"{indicators[indicator_id]} in {countries[country_id]}",
                      labels={'value': indicators[indicator_id], 'year': 'Year'},
                      markers=True)
        fig.update_traces(line=dict(width=2), marker=dict(size=5))
        fig.update_layout(hovermode='x unified', showlegend=False)
        st.plotly_chart(fig)

        # Display the URL below the graph
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}"
        st.markdown(f"**Data available at:** [API URL]({url})")

        # Button to download the CSV
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"{countries[country_id]}_{indicators[indicator_id]}.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data available for the selected year range.")
else:
    st.warning("No data available for the selected country and indicator.")
