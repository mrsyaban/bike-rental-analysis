import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    hour_df = pd.read_csv('data/hour.csv')
    day_df = pd.read_csv('data/day.csv')
    
    # Convert date columns
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    
    return hour_df, day_df

hour_df, day_df = load_data()

# Title
st.title("🚲 Bike Rental Analysis Dashboard")

# Date range filter
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(hour_df['dteday'].min(), hour_df['dteday'].max()),
    min_value=hour_df['dteday'].min(),
    max_value=hour_df['dteday'].max()
)

# Filter data based on date range
filtered_df = hour_df[
    (hour_df['dteday'].dt.date >= date_range[0]) &
    (hour_df['dteday'].dt.date <= date_range[1])
]

# Metrics for selected period
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Users", f"{filtered_df['cnt'].sum():,}")
with col2:
    st.metric("Casual Users", f"{filtered_df['casual'].sum():,}")
with col3:
    st.metric("Registered Users", f"{filtered_df['registered'].sum():,}")

# Time series plot
st.subheader("Rental Trends Over Time")
daily_data = filtered_df.groupby(['dteday', 'workingday']).agg({
    'casual': 'sum',
    'registered': 'sum',
    'cnt': 'sum'
}).reset_index()

fig = go.Figure()

# Add traces for total users
fig.add_trace(
    go.Scatter(
        x=daily_data['dteday'],
        y=daily_data['cnt'],
        name="Total Users",
        mode='markers',
        marker=dict(
            color=daily_data['workingday'].map({1: 'blue', 0: 'red'}),
            size=8
        ),
        hovertemplate="<b>Date:</b> %{x}<br>" +
                      "<b>Total Users:</b> %{y}<br>" +
                      "<b>Day Type:</b> %{text}<extra></extra>",
        text=daily_data['workingday'].map({1: 'Working Day', 0: 'Non-working Day'})
    )
)

fig.update_layout(
    title="Daily Bike Rentals (Blue: Working Day, Red: Non-working Day)",
    xaxis_title="Date",
    yaxis_title="Number of Rentals",
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# Weather analysis
st.subheader("Weather Impact Analysis")

# Weather description mapping
weather_desc = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Snow"
}

# Add weather description column
filtered_df['weather_desc'] = filtered_df['weathersit'].map(weather_desc)

# Create tabs for different weather visualizations
tab1, tab2 = st.tabs(["Average Rentals by Weather", "Weather Distribution"])

with tab1:
    # Calculate average rentals by weather
    weather_avg = filtered_df.groupby('weather_desc').agg({
        'casual': 'mean',
        'registered': 'mean',
        'cnt': 'mean'
    }).round(2)

    # Create bar chart
    fig_weather = px.bar(
        weather_avg,
        barmode='group',
        title="Average Rentals by Weather Condition",
        labels={'value': 'Average Number of Rentals', 'variable': 'User Type'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    st.plotly_chart(fig_weather, use_container_width=True)

with tab2:
    # Create scatter plot of temperature vs rentals colored by weather
    fig_scatter = px.scatter(
        filtered_df,
        x='temp',
        y='cnt',
        color='weather_desc',
        title="Temperature vs Total Rentals by Weather Condition",
        labels={
            'temp': 'Temperature (Normalized)',
            'cnt': 'Total Rentals',
            'weather_desc': 'Weather Condition'
        },
        opacity=0.6
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)

# Add correlation heatmap for weather-related variables
st.subheader("Weather Factors Correlation")
weather_vars = ['temp', 'atemp', 'hum', 'windspeed', 'cnt']
corr_matrix = filtered_df[weather_vars].corr()

fig_corr = px.imshow(
    corr_matrix,
    labels=dict(color="Correlation"),
    color_continuous_scale="RdBu",
    title="Correlation between Weather Factors and Rentals"
)

st.plotly_chart(fig_corr, use_container_width=True)