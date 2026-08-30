import streamlit as st
import pandas as pd
import plotly.express as px
import csv
st.set_page_config(
    page_title="Supply Chain Analysis",
    page_icon="📦",
    layout="wide"
)

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "APL_Logistics_Final_Cleaned1.csv",
        quoting=csv.QUOTE_NONE
    )

    # Remove extra quotes and spaces
    df = df.map(
        lambda x: x.strip().strip('"').strip("'")
        if isinstance(x, str) else x
    )

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.strip('"')
        .str.strip("'")
    )

    # Convert numeric columns where possible
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() == df[col].notna().sum():
            df[col] = converted

    return df

df = load_data()
st.write("DEBUG COLUMNS:", df.columns.tolist())

# -----------------------------
# Title
# -----------------------------
st.title("📦 Supply Chain Analysis Dashboard")
st.markdown(
    "Customer, Product, Sales & Profitability Performance Analysis"
)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Filters")

market = st.sidebar.multiselect(
    "Market",
    options=sorted(df["Market"].dropna().unique()),
    default=sorted(df["Market"].dropna().unique())
)

segment = st.sidebar.multiselect(
    "Customer Segment",
    options=sorted(df["Customer Segment"].dropna().unique()),
    default=sorted(df["Customer Segment"].dropna().unique())
)

shipping = st.sidebar.multiselect(
    "Shipping Mode",
    options=sorted(df["Shipping Mode"].dropna().unique()),
    default=sorted(df["Shipping Mode"].dropna().unique())
)

filtered_df = df[
    (df["Market"].isin(market)) &
    (df["Customer Segment"].isin(segment)) &
    (df["Shipping Mode"].isin(shipping))
]

# -----------------------------
# KPI Section
# -----------------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Benefit per order"].sum()
total_orders = filtered_df["Order Customer Id"].nunique()
avg_shipping_delay = filtered_df["Shipping_Delay"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
col3.metric("📦 Total Orders", f"{total_orders:,}")
col4.metric("🚚 Avg Shipping Delay", f"{avg_shipping_delay:.2f} days")

st.divider()

# -----------------------------
# Charts Row 1
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    sales_market = (
        filtered_df.groupby("Market")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )

    fig = px.bar(
        sales_market,
        x="Market",
        y="Sales",
        title="Sales by Market"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    category_sales = (
        filtered_df.groupby("Category Name")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    fig = px.bar(
        category_sales,
        x="Sales",
        y="Category Name",
        orientation="h",
        title="Top 10 Categories by Sales"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Charts Row 2
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    shipping_sales = (
        filtered_df.groupby("Shipping Mode")["Sales"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        shipping_sales,
        names="Shipping Mode",
        values="Sales",
        title="Sales by Shipping Mode"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    delivery_status = (
        filtered_df["Delivery Status"]
        .value_counts()
        .reset_index()
    )

    delivery_status.columns = ["Delivery Status", "Count"]

    fig = px.pie(
        delivery_status,
        names="Delivery Status",
        values="Count",
        title="Delivery Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Product Performance
# -----------------------------
st.subheader("🏆 Top Products")

product_sales = (
    filtered_df.groupby("Product Name")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
    .head(10)
)

fig = px.bar(
    product_sales,
    x="Sales",
    y="Product Name",
    orientation="h",
    title="Top 10 Products by Sales"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Data Preview
# -----------------------------
st.subheader("📊 Dataset Preview")

st.dataframe(
    filtered_df.head(100),
    use_container_width=True
)

st.caption(
    f"Showing {len(filtered_df):,} filtered records out of {len(df):,} total records."
)