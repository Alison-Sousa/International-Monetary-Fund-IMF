import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Title of the application
st.title("IMF Economic Indicators Dashboard")

# Add the logo.svg image in the sidebar
st.sidebar.image("logo.svg", use_column_width=True)

# Function to get the list of datasets (Dataflow)
@st.cache_data
def get_datasets():
    """Get the list of datasets from the IMF."""
    url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch datasets: {response.status_code} - {response.text}")
        return {}
    
    try:
        data = response.json()
        datasets = {ds['@id']: ds['Name']['#text'] for ds in data['Structure']['Dataflows']['Dataflow']}
        return datasets
    except ValueError as e:
        st.error(f"Error parsing JSON response for datasets: {e}")
        return {}

# Function to get the list of dimensions for a dataset (DataStructure)
@st.cache_data
def get_dimensions(dataset_id):
    """Get the list of dimensions for a dataset from the IMF."""
    url = f"http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/{dataset_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch dimensions: {response.status_code} - {response.text}")
        return {}
    
    try:
        data = response.json()
        dimensions = {dim['@id']: dim['Name']['#text'] for dim in data['Structure']['KeyFamilies']['KeyFamily']['Components']['Dimension']}
        return dimensions
    except ValueError as e:
        st.error(f"Error parsing JSON response for dimensions: {e}")
        return {}

# Function to get data from the IMF (CompactData)
@st.cache_data
def get_indicator_data(dataset_id, dimension_id, start_year, end_year):
    """Get data for a specific indicator from the IMF."""
    try:
        url = f"http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/{dataset_id}/A.{dimension_id}?startPeriod={start_year}&endPeriod={end_year}"
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
        if 'CompactData' in data and 'DataSet' in data['CompactData']:
            series = data['CompactData']['DataSet']['Series']
            if isinstance(series, list):
                df_list = []
                for s in series:
                    obs = s['Obs']
                    df_temp = pd.DataFrame(obs)
                    df_temp['@TIME_PERIOD'] = pd.to_numeric(df_temp['@TIME_PERIOD'])
                    df_temp['@OBS_VALUE'] = pd.to_numeric(df_temp['@OBS_VALUE'])
                    df_temp.rename(columns={'@TIME_PERIOD': 'year', '@OBS_VALUE': 'value'}, inplace=True)
                    df_list.append(df_temp)
                df = pd.concat(df_list, ignore_index=True)
                return df
            else:
                obs = series['Obs']
                df = pd.DataFrame(obs)
                df['@TIME_PERIOD'] = pd.to_numeric(df['@TIME_PERIOD'])
                df['@OBS_VALUE'] = pd.to_numeric(df['@OBS_VALUE'])
                df.rename(columns={'@TIME_PERIOD': 'year', '@OBS_VALUE': 'value'}, inplace=True)
                return df
        else:
            st.error("Error: No data available for the selected dataset and dimension.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error while obtaining data: {e}")
        return pd.DataFrame()

# Sidebar for selecting datasets and dimensions
st.sidebar.header("Search Settings")
datasets = get_datasets()
dataset_id = st.sidebar.selectbox("Select a Dataset:", options=list(datasets.keys()), format_func=lambda x: datasets[x])

dimensions = get_dimensions(dataset_id)
dimension_id = st.sidebar.selectbox("Select a Dimension:", options=list(dimensions.keys()), format_func=lambda x: dimensions[x])

# Automatically obtain data upon changing selections
start_year = st.sidebar.number_input("Start Year:", value=2000, min_value=1900, max_value=2100)
end_year = st.sidebar.number_input("End Year:", value=2023, min_value=1900, max_value=2100)

df = get_indicator_data(dataset_id, dimension_id, start_year, end_year)

if not df.empty:
    # Plot the interactive graph
    fig = px.line(df, x='year', y='value', 
                  title=f"{dimensions[dimension_id]} in {datasets[dataset_id]}",
                  labels={'value': dimensions[dimension_id], 'year': 'Year'},
                  markers=True)
    fig.update_traces(line=dict(width=2), marker=dict(size=5))
    fig.update_layout(hovermode='x unified', showlegend=False)
    st.plotly_chart(fig)

    # Display the URL below the graph
    url = f"http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/{dataset_id}/A.{dimension_id}?startPeriod={start_year}&endPeriod={end_year}"
    st.markdown(f"**Data available at:** [API URL]({url})")

    # Button to download the CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f"{datasets[dataset_id]}_{dimensions[dimension_id]}.csv",
        mime="text/csv",
    )
else:
    st.warning("No data available for the selected dataset and dimension.")
