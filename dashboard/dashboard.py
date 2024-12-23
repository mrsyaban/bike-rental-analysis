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

def categorize(row):
    if row['weathersit'] == 1 and row['temp'] > 0.6 and row['hum'] < 0.5:
        return 'Ideal'
    elif row['weathersit'] in [1, 2] and row['temp'] > 0.4 and row['hum'] < 0.7:
        return 'Good'
    elif row['weathersit'] in [2, 3] and row['temp'] > 0.2 and row['hum'] < 0.8:
        return 'Moderate'
    else:
        return 'Poor'

hour_df, day_df = load_data()

# Title
st.title("🚲 Bike Rental Analysis Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(hour_df['dteday'].min(), hour_df['dteday'].max()),
    min_value=hour_df['dteday'].min(),
    max_value=hour_df['dteday'].max()
)

# Add user type filter
user_type = st.sidebar.selectbox(
    "Select User Type",
    ["All", "Casual", "Registered"]
)

filtered_df = hour_df[
    (hour_df['dteday'].dt.date >= date_range[0]) &
    (hour_df['dteday'].dt.date <= date_range[1])
]

st.subheader("Working days Impact Analysis")
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

# Modify the chart based on user type selection
if user_type == "All":
    y_column = 'cnt'
    title_suffix = "Total"
elif user_type == "Casual":
    y_column = 'casual'
    title_suffix = "Casual"
else:
    y_column = 'registered'
    title_suffix = "Registered"

fig.add_trace(
    go.Scatter(
        x=daily_data[daily_data['workingday'] == 1]['dteday'],
        y=daily_data[daily_data['workingday'] == 1][y_column],
        name="Working Day",
        mode='markers',
        marker=dict(color='blue', size=8),
        hovertemplate="<b>Date:</b> %{x}<br><b>Users:</b> %{y}<br><b>Day Type:</b> Working Day<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=daily_data[daily_data['workingday'] == 0]['dteday'],
        y=daily_data[daily_data['workingday'] == 0][y_column],
        name="Non-working Day",
        mode='markers',
        marker=dict(color='red', size=8),
        hovertemplate="<b>Date:</b> %{x}<br><b>Users:</b> %{y}<br><b>Day Type:</b> Non-working Day<extra></extra>"
    )
)

fig.update_layout(
    title=f"Daily Bike Rentals - {title_suffix} Users",
    xaxis_title="Date",
    yaxis_title=f"Number of {title_suffix} Rentals",
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

# Weather Impact Analysis
st.subheader("Weather Impact Analysis")

weather_desc = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Ice Pallets"
}

filtered_df['weather_desc'] = filtered_df['weathersit'].map(weather_desc)

tab1, tab2, tab3, tab4 = st.tabs(["Average Rentals by Weather", "Weather Factors vs Rentals", 
                                 "Weather Rentals Correlation", "Advanced Analysis"])

# Box Plot
with tab1:
    fig_weather = px.box(
        filtered_df,
        x='weather_desc',
        y=['casual', 'registered', 'cnt'],
        title="Rental Distribution by Weather Condition",
        labels={'value': 'Number of Rentals', 'variable': 'User Type'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_weather, use_container_width=True)

with tab2:
    # Temperature plot
    fig_temp = px.scatter(
        filtered_df,
        x='temp',
        y='cnt',
        color='weather_desc',
        title="Temperature vs Total Rentals",
        labels={
            'temp': 'Temperature (Normalized)',
            'cnt': 'Total Rentals',
            'weather_desc': 'Weather Condition'
        },
        opacity=0.6
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # Humidity plot
    fig_hum = px.scatter(
        filtered_df,
        x='hum',
        y='cnt',
        color='weather_desc',
        title="Humidity vs Total Rentals",
        labels={
            'hum': 'Humidity (Normalized)',
            'cnt': 'Total Rentals',
            'weather_desc': 'Weather Condition'
        },
        opacity=0.6
    )
    st.plotly_chart(fig_hum, use_container_width=True)
    
    # Wind speed plot
    fig_wind = px.scatter(
        filtered_df,
        x='windspeed',
        y='cnt',
        color='weather_desc',
        title="Wind Speed vs Total Rentals",
        labels={
            'windspeed': 'Wind Speed (Normalized)',
            'cnt': 'Total Rentals',
            'weather_desc': 'Weather Condition'
        },
        opacity=0.6
    )
    st.plotly_chart(fig_wind, use_container_width=True)

with tab3:
    weather_vars = ['temp', 'atemp', 'hum', 'windspeed', 'cnt']
    corr_matrix = filtered_df[weather_vars].corr()

    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        color_continuous_scale="RdBu",
        title="Correlation between Weather Factors and Rentals"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with tab4:
    # Add weather category
    filtered_df['weather_category'] = filtered_df.apply(categorize, axis=1)
    
    fig_category = px.box(
        filtered_df,
        x='weather_category',
        y=['casual', 'registered', 'cnt'],
        title="Rental Distribution by Weather Category",
        labels={'value': 'Number of Rentals', 'variable': 'User Type'},
        color_discrete_sequence=px.colors.qualitative.Set3,
        category_orders={"weather_category": ["Ideal", "Good", "Moderate", "Poor"]}
    )
    st.plotly_chart(fig_category, use_container_width=True)

    # Legend
    st.markdown("""
    ### Weather Category Criteria:

    1. "Ideal" Category:\n
        weather situation must = 1 (meaning clear)\n
        temperature must be > 0.6 (fairly warm)\n
        humidity must be < 0.5 (not too humid)\n

    2. "Good" Category:\n
        weather situation must be 1 or 2 (clear or light clouds)\n
        temperature must be > 0.4 (fairly warm but not as hot as Ideal)\n
        humidity must be < 0.7 (moderate humidity)\n

    3. "Moderate" Category:\n
        weather situation can be 2 or 3 (light clouds or heavy clouds)\n
        temperature must be > 0.2 (minimum warmth)\n
        humidity must be < 0.8 (can have higher humidity)\n

    4. "Poor" Category:\n
        If conditions don't meet any of the above criteria, it falls into the Poor category
    """)