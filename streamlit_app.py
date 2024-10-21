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
    data = response.json()
    countries = {key: value['label'] for key, value in data['countries'].items()}
    return countries

# Function to get the list of indicators
@st.cache_data
def get_indicators():
    """Get the list of indicators from the IMF."""
    url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    response = requests.get(url)
    data = response.json()
    indicators = {key: value['label'] for key, value in data['indicators'].items()}
    return indicators

# Function to get data from the IMF
@st.cache_data
def get_indicator_data(country_id, indicator_id, start_year, end_year):
    """Get data for a specific indicator for a country from the IMF."""
    try:
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
        print(f"Requesting URL: {url}")  # Log the request URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            st.error(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")  # Log the response text for debugging
            return pd.DataFrame()

        # Check if the response is empty
        if not response.text:
            st.error("Error: Received empty response.")
            return pd.DataFrame()

        # Try to parse the JSON response
        try:
            data = response.json()
        except ValueError:
            st.error("Error: Unable to parse JSON response.")
            print(f"Response content: {response.text}")  # Log the raw response content
            return pd.DataFrame()

        # Check if the data is present
        if "values" in data and indicator_id in data["values"] and country_id in data["values"][indicator_id]:
            years_data = data["values"][indicator_id][country_id]
            # Convert the data into a DataFrame
            df = pd.DataFrame(years_data.items(), columns=['year', 'value'])
            df['year'] = pd.to_numeric(df['year'])
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if there are no data
    except Exception as e:
        st.error(f"Error while obtaining data: {e}")
        return pd.DataFrame()

# Sidebar for selecting countries, indicators, and years
st.sidebar.header("Search Settings")
countries = get_countries()
country_id = st.sidebar.selectbox("Select a Country:", options=list(countries.keys()), format_func=lambda x: countries[x])

indicators = get_indicators()
indicator_id = st.sidebar.selectbox("Select an Indicator:", options=list(indicators.keys()), format_func=lambda x: indicators[x])

start_year = st.sidebar.number_input("Start Year:", value=2000, min_value=1900, max_value=2024)
end_year = st.sidebar.number_input("End Year:", value=2024, min_value=1900, max_value=2024)

# Automatically obtain data upon changing selections
df = get_indicator_data(country_id, indicator_id, start_year, end_year)
if not df.empty:
    # Filter the data according to the selected year range
    df_filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
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
        url = f"https://www.imf.org/external/datamapper/api/v1/data/{indicator_id}/{country_id}/{start_year}/{end_year}"
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
