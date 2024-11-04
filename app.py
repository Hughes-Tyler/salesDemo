import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta
import plotly.express as px

# Set page layout to wide
st.set_page_config(layout="wide")

st.title("Sales Demo Dashboard by Hues Analytics")
# Load the dataset with improved encoding
@st.cache_data
def load_data():
    file_path = "Global_Superstore4.csv"
    data = pd.read_csv(file_path, encoding='ISO-8859-1', parse_dates=['Order Date'])
    data['Order Date'] = pd.to_datetime(data['Order Date'], dayfirst=True, errors='coerce')

    return data

# Load data
data = load_data()


# Calculate minimum and maximum dates
min_date = pd.to_datetime(data['Order Date'].min()).date()
max_date = pd.to_datetime(data['Order Date'].max()).date()

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
        delta_color = "green" if delta >= 0 else "red"

        # Render bordered card
        st.markdown(
            f"""
            <div class="metric-card" style="border: 1px solid #e1e1e1; padding: 10px; border-radius: 5px;">
                <h3 style="margin-bottom: 5px;">{label}</h3>
                <div class="metric-value" style="font-size: 24px; font-weight: bold;">{format_func(value)}</div>
                <div class="metric-delta" style="color: {delta_color}; font-size: 16px;">
                    {delta:.2f}% to prev. period
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
st.write("\n")


################################################
### Row 3 - Period detail
################################################

st.write("\n")
st.write("\n")

st.subheader("Category Analysis")
# Create two columns for side-by-side charts
col1, spacer, col2 = st.columns([1, 0.1, 1])

# Sales and Profit by Product Category Analysis
with col1:
    # Group by Category and Sub-Category
    category_analysis = data.groupby(['Category', 'Sub-Category']).agg(
        total_sales=pd.NamedAgg(column='Sales', aggfunc='sum'),
        total_profit=pd.NamedAgg(column='Profit', aggfunc='sum')
    ).reset_index()
    
    # Calculate profit margin for each sub-category
    category_analysis['profit_margin'] = (category_analysis['total_profit'] / category_analysis['total_sales']) * 100
    
    # Bar chart for Sales and Profit by Category
    fig_category_sales = px.bar(
        category_analysis, 
        x='Sub-Category', 
        y=['total_sales', 'total_profit'],
        color='Category',
        barmode='group',
        labels={'value': 'Amount ($)', 'variable': 'Metric'},
        title="Sales and Profit by Product Category"
    )
    fig_category_sales.update_layout(
    legend=dict(
        orientation="h",  # Horizontal legend
        yanchor="bottom",  # Align legend to the bottom of the container
        y=1.02,  # Slightly above the chart
        xanchor="center",  # Center the legend horizontally
        x=0.5  # Position in the middle of the chart
        ),
        legend_title_text=""
    )
    
    st.plotly_chart(fig_category_sales, use_container_width=True)
    st.write("Detailed Category Analysis")
    st.dataframe(category_analysis[['Category', 'Sub-Category', 'total_sales', 'total_profit', 'profit_margin']])

# Regional Sales Performance Analysis
with col2:
    # Group by Region and Country
    regional_analysis = data.groupby(['Region']).agg(
        total_sales=pd.NamedAgg(column='Sales', aggfunc='sum'),
        total_profit=pd.NamedAgg(column='Profit', aggfunc='sum'),
        num_orders=pd.NamedAgg(column='Order ID', aggfunc='nunique')
    ).reset_index()
    
    # Calculate profit margin and average order value for each region and country
    regional_analysis['profit_margin'] = (regional_analysis['total_profit'] / regional_analysis['total_sales']) * 100
    regional_analysis['avg_order_value'] = regional_analysis['total_sales'] / regional_analysis['num_orders']
    
    # Bar chart for Sales by Region
    fig_region_sales = px.bar(
        regional_analysis, 
        x='Region', 
        y='total_sales', 
        color ='Region',
        labels={'total_sales': 'Total Sales ($)', 'Region': 'Region'},
        title="Total Sales by Region"
    )
    st.plotly_chart(fig_region_sales, use_container_width=True)

    # Display data as a table for additional insights
    st.write("Detailed Regional Analysis")
    st.dataframe(regional_analysis[['Region', 'total_sales', 'total_profit', 'profit_margin', 'avg_order_value']])

################################################
### Row 4 - Order details
################################################

# Filter data based on the selected date range for order details
order_details_data = data[(data['Order Date'] >= start_date) & (data['Order Date'] <= selected_day)]

# Display filtered order details in a centered dataframe
st.write("\n")
st.write("\n")

st.subheader("Order Details", anchor=False)

st.dataframe(
    order_details_data,
    hide_index=True,
    use_container_width=True,
    key="order_details",
)