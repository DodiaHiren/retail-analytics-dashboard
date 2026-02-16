import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import io

# Page config (professional look)
st.set_page_config(
    page_title="Global Retail Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for industrial look
st.markdown("""
<style>
.main {padding: 2rem 2rem;}
.block-container {padding-top: 2rem;}
h1 {color: #1f77b4;}
.metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# Generate realistic retail sales data
@st.cache_data
def load_data():
    np.random.seed(42)
    n_days = 365
    dates = pd.date_range(start="2025-01-01", periods=n_days)
    data = {
        "Date": np.tile(dates, 100),
        "Order_ID": range(1, n_days * 100 + 1),
        "Customer_ID": np.random.randint(1000, 5000, n_days * 100),
        "Region": np.random.choice(["North America", "Europe", "Asia", "LATAM"], n_days * 100),
        "Category": np.random.choice(["Electronics", "Clothing", "Home", "Books"], n_days * 100),
        "Product": np.random.choice(["iPhone", "T-Shirt", "Sofa", "Novel"], n_days * 100),
        "Quantity": np.random.randint(1, 10, n_days * 100),
        "Unit_Price": np.random.uniform(10, 1000, n_days * 100),
        "Discount": np.random.uniform(0, 0.3, n_days * 100)
    }
    df = pd.DataFrame(data)
    df['Revenue'] = df['Quantity'] * df['Unit_Price'] * (1 - df['Discount'])
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Load data
df = load_data()

st.title("🛒 Global Retail Analytics Dashboard")
st.markdown("**Interactive analytics platform for retail sales data** | *Production-ready*")

# Sidebar: Advanced filters
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(df['Date'].min(), df['Date'].max()),
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)
regions = st.sidebar.multiselect("Region", options=df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Category", options=df['Category'].unique(), default=df['Category'].unique())

# Filter data
filtered_df = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Region'].isin(regions)) &
    (df['Category'].isin(categories))
]

# KPIs Row 1
col1, col2, col3, col4 = st.columns(4)
kpi_revenue = filtered_df['Revenue'].sum()
kpi_orders = len(filtered_df)
kpi_customers = filtered_df['Customer_ID'].nunique()
kpi_avg_order = kpi_revenue / kpi_orders if kpi_orders > 0 else 0

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Total Revenue", f"${kpi_revenue:,.0f}", delta="12%")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📦 Total Orders", f"{kpi_orders:,}", delta="8%")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("👥 Unique Customers", f"{kpi_customers:,}", delta="5%")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💵 Avg Order Value", f"${kpi_avg_order:.0f}", delta="4%")
    st.markdown('</div>', unsafe_allow_html=True)

# Charts Row
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Revenue Trend")
    daily_revenue = filtered_df.groupby(filtered_df['Date'].dt.date)['Revenue'].sum().reset_index()
    fig1 = px.line(daily_revenue, x='Date', y='Revenue', title="Daily Revenue")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🌍 Revenue by Region")
    region_rev = filtered_df.groupby('Region')['Revenue'].sum().reset_index()
    fig2 = px.bar(region_rev, x='Region', y='Revenue', title="Regional Performance")
    st.plotly_chart(fig2, use_container_width=True)

# Data table with download
st.subheader("📋 Detailed Sales Data")
st.dataframe(filtered_df[['Date', 'Region', 'Category', 'Product', 'Quantity', 'Unit_Price', 'Revenue']].head(1000), use_container_width=True)

# Download button
csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv_buffer.getvalue(),
    file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Bottom metrics
col1, col2, col3 = st.columns(3)
col1.metric("🎯 Top Category Revenue", f"{filtered_df.groupby('Category')['Revenue'].sum().max():.0f}")
col2.metric("🏆 Top Region", filtered_df.groupby('Region')['Revenue'].sum().idxmax())
col3.metric("📱 Busiest Day", filtered_df.groupby(filtered_df['Date'].dt.date)['Revenue'].sum().idxmax().strftime('%Y-%m-%d'))
