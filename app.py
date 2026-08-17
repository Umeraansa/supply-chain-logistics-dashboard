import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Layout & Config
st.set_page_config(page_title="Global Supply Chain & Logistics Dashboard", page_icon="📦", layout="wide")

st.title("📦 Global E-Commerce Supply Chain & Fulfillment Dashboard")
st.markdown("Monitor order fulfillment performance, carrier delivery times, shipping costs, and operational bottlenecks.")

# Generate Simulated Global Logistics Dataset
@st.cache_data
def load_logistics_data():
    np.random.seed(42)
    n_rows = 1000
    
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"]
    carriers = ["FedEx Express", "DHL Global", "UPS Standard", "Local Courier"]
    shipping_modes = ["Air Priority", "Standard Ground", "Ocean Freight"]
    
    data = {
        "Order_ID": [f"ORD-{i:05d}" for i in range(1, n_rows + 1)],
        "Region": np.random.choice(regions, n_rows),
        "Carrier": np.random.choice(carriers, n_rows),
        "Shipping_Mode": np.random.choice(shipping_modes, n_rows),
        "Shipping_Cost": np.random.uniform(5.0, 85.0, n_rows),
        "Transit_Days": np.random.randint(1, 15, n_rows),
        "Delay_Status": np.random.choice(["On-Time", "Delayed"], n_rows, p=[0.78, 0.22]),
        "Order_Value": np.random.uniform(25.0, 500.0, n_rows)
    }
    return pd.DataFrame(data)

df = load_logistics_data()

# Sidebar Filters for Business Users
st.sidebar.header("🔍 Filter Logistics Data")
selected_region = st.sidebar.selectbox("Select Destination Region", ["All"] + list(df["Region"].unique()))
selected_carrier = st.sidebar.selectbox("Select Logistics Carrier", ["All"] + list(df["Carrier"].unique()))

# Apply Filters
filtered_df = df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_carrier != "All":
    filtered_df = filtered_df[filtered_df["Carrier"] == selected_carrier]

# Executive Summary Metrics
st.subheader("📊 Operational Executive Summary")
total_orders = len(filtered_df)
avg_transit = round(filtered_df["Transit_Days"].mean(), 1)
total_shipping_spend = round(filtered_df["Shipping_Cost"].sum(), 2)
delayed_orders_pct = round((len(filtered_df[filtered_df["Delay_Status"] == "Delayed"]) / total_orders) * 100, 1) if total_orders > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tracked Orders", f"{total_orders:,}")
m2.metric("Avg. Transit Time", f"{avg_transit} Days")
m3.metric("Total Shipping Spend", f"${total_shipping_spend:,.2f}")
m4.metric("Delay Rate (%)", f"{delayed_orders_pct}%", delta="Target < 15%" if delayed_orders_pct < 15 else "High Delay Alert", delta_color="inverse")

st.markdown("---")

# Visualizations Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚚 Transit Time by Shipping Mode")
    fig_mode = px.box(filtered_df, x="Shipping_Mode", y="Transit_Days", color="Shipping_Mode", 
                      title="Distribution of Delivery Days Across Shipping Methods")
    st.plotly_chart(fig_mode, use_container_width=True)

with col2:
    st.markdown("### 🌍 Regional Order Volume & Bottlenecks")
    region_grouped = filtered_df.groupby(["Region", "Delay_Status"]).size().reset_index(name="Count")
    fig_region = px.bar(region_grouped, x="Region", y="Count", color="Delay_Status", barmode="group",
                        title="On-Time vs Delayed Orders by Region")
    st.plotly_chart(fig_region, use_container_width=True)

# Visualizations Row 2
st.markdown("### 📋 Carrier Cost & Performance Matrix")
carrier_summary = filtered_df.groupby("Carrier").agg(
    Total_Orders=("Order_ID", "count"),
    Avg_Shipping_Cost=("Shipping_Cost", "mean"),
    Avg_Transit_Days=("Transit_Days", "mean")
).reset_index()
carrier_summary["Avg_Shipping_Cost"] = carrier_summary["Avg_Shipping_Cost"].round(2)
carrier_summary["Avg_Transit_Days"] = carrier_summary["Avg_Transit_Days"].round(1)

st.dataframe(carrier_summary, hide_index=True)
st.info("💡 **Analyst Insight:** Carriers showing higher average transit days with elevated shipping costs should be flagged for contract renegotiation or volume reallocation.")
