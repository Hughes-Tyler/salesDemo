import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta

# Set page layout to wide
st.set_page_config(layout="wide")

# Load the dataset with improved encoding
@st.cache_data
def load_data():
    file_path = "Global_Superstore2.csv"
    data = pd.read_csv(file_path, encoding='ISO-8859-1', parse_dates=['Order Date'])
    return data

# Load data
data = load_data()

# Calculate minimum and maximum dates
min_date = data['Order Date'].min()
max_date = data['Order Date'].max()

# Configuration section with an expander
with st.expander("**Configuration**", icon="⚙"):
    configuration_row = st.columns([1, 1, 0.5, 1.5], gap="large")
    
    selected_day = configuration_row[0].date_input(
        "End date", value=max_date, min_value=min_date, max_value=max_date
    )
    
    selected_period = configuration_row[1].selectbox(
        "Analysis Period", [7, 28, 90, 365], index=1, format_func=lambda n: f"{n} days"
    )
    
    # Convert selected_day to datetime and calculate start_date as datetime
    selected_day = pd.to_datetime(selected_day)
    start_date = selected_day - timedelta(days=selected_period)
    
    configuration_row[3].subheader(
        f"Period: {start_date} -> {selected_day}"
    )
    
    st.write("Analysis Start Date:", start_date)
    st.write("Selected End Date:", selected_day)
    st.write("Selected Analysis Period:", f"{selected_period} days")

################################################
### Row 2 - Row Card KPIs
################################################

# Filter data based on the selected date range
filtered_data = data[(data['Order Date'] >= start_date) & (data['Order Date'] <= selected_day)]

# Calculate KPIs for the current period
n_orders = filtered_data['Order ID'].nunique()
n_customers = filtered_data['Customer ID'].nunique()
sales = filtered_data['Sales'].sum()
profit = filtered_data['Profit'].sum()
profit_ratio = 100 * profit / sales if sales != 0 else 0

# Calculate KPIs for the previous period
previous_period_data = data[(data['Order Date'] >= start_date - timedelta(days=selected_period)) & 
                            (data['Order Date'] < start_date)]
n_orders_previous_period = previous_period_data['Order ID'].nunique()
n_customers_previous_period = previous_period_data['Customer ID'].nunique()
sales_previous_period = previous_period_data['Sales'].sum()
profit_previous_period = previous_period_data['Profit'].sum()
profit_ratio_previous_period = 100 * profit_previous_period / sales_previous_period if sales_previous_period != 0 else 0

# Helper function to compute percentage delta
def compute_delta(current_value, previous_value):
    if previous_value == 0:
        return 0  # Avoid division by zero
    return ((current_value - previous_value) / previous_value) * 100

# Display KPI Overview
st.subheader("Overview", anchor=False)

# Create KPI cards with metrics and sparklines
cards_row = st.container()
with cards_row:
    cards_columns = st.columns(4)

# Define labels, values, previous values, and formatting for KPIs
kpi_data = [
    ("Number Orders", n_orders, n_orders_previous_period, lambda value: value, 'Order ID'),
    ("Total Sales", sales, sales_previous_period, lambda value: f"{value:,.2f} $".replace(",", " "), 'Sales'),
    ("Total Profit", profit, profit_previous_period, lambda value: f"{value:,.2f} $".replace(",", " "), 'Profit'),
    ("Profit Ratio", profit_ratio, profit_ratio_previous_period, lambda value: f"{value:,.2f} %".replace(",", " "), 'Profit')
]

for (label, value, previous_value, format_func, column_name), column in zip(kpi_data, cards_columns):
    with column.container():
        card = st.columns((1, 1))
        
        with card[0]:
            st.metric(
                label=label,
                value=format_func(value),
                delta=f"{compute_delta(value, previous_value):.2f}% to prev. period"
            )
        with card[1]:
            # Generate sparkline data using the specified column name
            fig = go.Figure(go.Scatter(
                x=filtered_data['Order Date'],
                y=filtered_data[column_name],  # Using the exact column name
                mode="lines+markers"
            ))
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=50)
            
            # Assign a unique key to each chart
            st.plotly_chart(
                fig,
                use_container_width=True,
                config=dict(displayModeBar=False),
                key=f"sparkline_{label}"
            )
