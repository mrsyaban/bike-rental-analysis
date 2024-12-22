import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

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

# PERTANYAAN 1
# Date range filter
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(hour_df['dteday'].min(), hour_df['dteday'].max()),
    min_value=hour_df['dteday'].min(),
    max_value=hour_df['dteday'].max()
)

filtered_df = hour_df[
    (hour_df['dteday'].dt.date >= date_range[0]) &
    (hour_df['dteday'].dt.date <= date_range[1])
]

st.subheader("Working days Impact Analysis")
# # Time series plot for number of user
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Users", f"{filtered_df['cnt'].sum():,}")
with col2:
    st.metric("Casual Users", f"{filtered_df['casual'].sum():,}")
with col3:
    st.metric("Registered Users", f"{filtered_df['registered'].sum():,}")


daily_data = filtered_df.groupby(['dteday', 'workingday']).agg({
    'casual': 'sum',
    'registered': 'sum',
    'cnt': 'sum'
}).reset_index()

fig = go.Figure()

# Add traces for working days and non-working days (holiday or weekend) separately
fig.add_trace(
    go.Scatter(
        x=daily_data[daily_data['workingday'] == 1]['dteday'],
        y=daily_data[daily_data['workingday'] == 1]['cnt'],
        name="Working Day",
        mode='markers',
        marker=dict(color='blue', size=8),
        hovertemplate="<b>Date:</b> %{x}<br>" +
                      "<b>Total Users:</b> %{y}<br>" +
                      "<b>Day Type:</b> Working Day<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=daily_data[daily_data['workingday'] == 0]['dteday'],
        y=daily_data[daily_data['workingday'] == 0]['cnt'],
        name="Non-working Day",
        mode='markers',
        marker=dict(color='red', size=8),
        hovertemplate="<b>Date:</b> %{x}<br>" +
                      "<b>Total Users:</b> %{y}<br>" +
                      "<b>Day Type:</b> Non-working Day<extra></extra>"
    )
)

fig.update_layout(
    title="Daily Bike Rentals",
    xaxis_title="Date",
    yaxis_title="Number of Rentals",
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.3)",
        borderwidth=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# PERTANYAAN 2
st.subheader("Weather Impact Analysis")

# Weather description mapping
weather_desc = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Ice Pallets"
}

filtered_df['weather_desc'] = filtered_df['weathersit'].map(weather_desc)

tab1, tab2, tab3 = st.tabs(["Average Rentals by Weather", "Weather Distribution", "Weather Rentals Correlation"])

# Bar Chart
with tab1:
    weather_avg = filtered_df.groupby('weather_desc').agg({
        'casual': 'mean',
        'registered': 'mean',
        'cnt': 'mean'
    }).round(2)

    fig_weather = px.bar(
        weather_avg,
        barmode='group',
        title="Average Rentals by Weather Condition",
        labels={'value': 'Average Number of Rentals', 'variable': 'User Type'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    st.plotly_chart(fig_weather, use_container_width=True)

# Scatter plot of temperature vs rentals colored by weather
with tab2:
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

with tab3:
    # Correlation heatmap for weather-related variables
    weather_vars = ['temp', 'atemp', 'hum', 'windspeed', 'cnt']
    corr_matrix = filtered_df[weather_vars].corr()

    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        color_continuous_scale="RdBu",
        title="Correlation between Weather Factors and Rentals"
    )

    st.plotly_chart(fig_corr, use_container_width=True)