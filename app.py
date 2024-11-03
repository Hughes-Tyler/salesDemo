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

st.markdown(
    """
    <style>
    .metric-card {
        border: 1px solid #e6e6e6;
        padding: 16px;
        border-radius: 8px;
        background-color: #f9f9f9;
        box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
        text-align: center;
    }
    .metric-card h3 {
        font-size: 1.2em;
        margin-bottom: 8px;
        color: #333333;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
    }
    .metric-delta {
        font-size: 1em;
        color: #666666;
    }
    </style>
    """,
    unsafe_allow_html=True
)
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

# Define labels, values, previous values, and formatting for KPIs
kpi_data = [
    ("Number of Orders", n_orders, n_orders_previous_period, lambda value: value),
    ("Total Sales", sales, sales_previous_period, lambda value: f"${value:,.2f}".replace(",", ",")),
    ("Total Profit", profit, profit_previous_period, lambda value: f"${value:,.2f}".replace(",", ",")),
    ("Profit Ratio", profit_ratio, profit_ratio_previous_period, lambda value: f"{value:,.2f} %".replace(",", ","))
]

# Create a row for KPI cards with bordered styles
cards_row = st.columns(4)

# Iterate over KPIs to create bordered metric cards
for (label, value, previous_value, format_func), column in zip(kpi_data, cards_row):
    with column:
        delta = compute_delta(value, previous_value)
        
        # Render bordered card
        st.markdown(
            f"""
            <div class="metric-card">
                <h3>{label}</h3>
                <div class="metric-value">{format_func(value)}</div>
                <div class="metric-delta">{delta:.2f}% to prev. period</div>
            </div>
            """,
            unsafe_allow_html=True
        )
st.write("\n")


################################################
### Row 3 - Period detail
################################################


st.subheader(
    "Category Analysis",
    anchor=False,
)