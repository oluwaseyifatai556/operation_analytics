import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Restaurant Ops Analytics", page_icon="🛵", layout="wide")

NAVY = "#1A3C5E"
ACCENT = "#E8833A"
BLUE = "#7A9CC6"
# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("train_cleaned.csv", parse_dates=["Order_Date"])
    return df

df = load_data()

# ---------- Header ----------
st.markdown(
    f"<h1 style='color:{NAVY}; margin-bottom:0;'>🛵 Restaurant & Food Delivery Operations Analytics</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Order volume, SLA compliance, and delivery performance — "
    "[Kaggle Food Delivery Dataset](https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset)"
)
st.divider()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

cities = sorted(df["City"].dropna().unique().tolist())
sel_cities = st.sidebar.multiselect("City type", cities, default=cities)

traffic_opts = ["Low", "Medium", "High", "Jam"]
traffic_opts = [t for t in traffic_opts if t in df["Road_traffic_density"].dropna().unique()]
sel_traffic = st.sidebar.multiselect("Traffic density", traffic_opts, default=traffic_opts)

weather_opts = sorted(df["Weatherconditions"].dropna().unique().tolist())
sel_weather = st.sidebar.multiselect("Weather", weather_opts, default=weather_opts)

festival_opts = sorted(df["Festival"].dropna().unique().tolist())
sel_festival = st.sidebar.multiselect("Festival day", festival_opts, default=festival_opts)

sla_threshold = st.sidebar.slider("SLA threshold (minutes)", 15, 45, 30, step=5)

date_min, date_max = df["Order_Date"].min().date(), df["Order_Date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)

# ---------- Apply filters ----------
mask = (
    df["City"].isin(sel_cities)
    & df["Road_traffic_density"].isin(sel_traffic)
    & df["Weatherconditions"].isin(sel_weather)
    & df["Festival"].isin(sel_festival)
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    mask &= (df["Order_Date"].dt.date >= date_range[0]) & (df["Order_Date"].dt.date <= date_range[1])

fdf = df[mask].copy()
fdf["SLA_Met_dynamic"] = fdf["Time_taken(min)"] <= sla_threshold

if fdf.empty:
    st.warning("No orders match the current filters. Adjust filters in the sidebar.")
    st.stop()

# ---------- KPI row ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{len(fdf):,}")
c2.metric("SLA Compliance", f"{fdf['SLA_Met_dynamic'].mean()*100:.1f}%")
c3.metric("Avg Delivery Time", f"{fdf['Time_taken(min)'].mean():.1f} min")
c4.metric("Median Delivery Time", f"{fdf['Time_taken(min)'].median():.1f} min")

st.divider()

# ---------- Row 1: order volume + delivery time distribution ----------
col1, col2 = st.columns(2)

with col1:
    weekly = fdf.groupby("Order_Week").size().reset_index(name="orders").sort_values("Order_Week")
    fig = px.line(weekly, x="Order_Week", y="orders", markers=True, title="Weekly Order Volume")
    fig.update_traces(line_color=NAVY)
    fig.update_layout(xaxis_title="Week", yaxis_title="Orders", title_font_color=NAVY)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(fdf, x="Time_taken(min)", nbins=30, title="Delivery Time Distribution")
    fig.update_traces(marker_color=NAVY)
    fig.add_vline(x=sla_threshold, line_dash="dash", line_color=ACCENT,
                   annotation_text=f"SLA threshold ({sla_threshold} min)")
    fig.update_layout(xaxis_title="Minutes", yaxis_title="Orders", title_font_color=NAVY)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Row 2: SLA by city + traffic ----------
col3, col4 = st.columns(2)

with col3:
    sla_city = fdf.groupby("City")["SLA_Met_dynamic"].mean().sort_values(ascending=False).reset_index()
    sla_city["SLA_Met_dynamic"] *= 100
    fig = px.bar(sla_city, x="City", y="SLA_Met_dynamic", title="SLA Compliance by City Type",
                 color_discrete_sequence=[NAVY])
    fig.update_layout(yaxis_title="% On-Time", xaxis_title="", title_font_color=NAVY)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    order = [t for t in ["Low", "Medium", "High", "Jam"] if t in fdf["Road_traffic_density"].unique()]
    sla_traffic = fdf.groupby("Road_traffic_density")["SLA_Met_dynamic"].mean().reindex(order).reset_index()
    sla_traffic["SLA_Met_dynamic"] *= 100
    fig = px.bar(sla_traffic, x="Road_traffic_density", y="SLA_Met_dynamic",
                 title="SLA Compliance by Traffic Density", color_discrete_sequence=[ACCENT])
    fig.update_layout(yaxis_title="% On-Time", xaxis_title="", title_font_color=NAVY)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Row 3: SLA by weather + vehicle type ----------
col5, col6 = st.columns(2)

with col5:
    sla_weather = fdf.groupby("Weatherconditions")["SLA_Met_dynamic"].mean().sort_values().reset_index()
    sla_weather["SLA_Met_dynamic"] *= 100
    fig = px.bar(sla_weather, x="SLA_Met_dynamic", y="Weatherconditions", orientation="h",
                 title="SLA Compliance by Weather", color_discrete_sequence=[NAVY])
    fig.update_layout(xaxis_title="% On-Time", yaxis_title="", title_font_color=NAVY)
    st.plotly_chart(fig, use_container_width=True)

with col6:
    sla_vehicle = fdf.groupby("Type_of_vehicle")["SLA_Met_dynamic"].mean().sort_values(ascending=False).reset_index()
    sla_vehicle["SLA_Met_dynamic"] *= 100
    fig = px.bar(sla_vehicle, x="Type_of_vehicle", y="SLA_Met_dynamic", title="SLA Compliance by Vehicle Type",
                 color_discrete_sequence=[BLUE])
    fig.update_layout(yaxis_title="% On-Time", xaxis_title="", title_font_color=NAVY)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Row 4: worst segments table ----------
st.divider()
st.subheader("Segments at Highest SLA Risk (City × Traffic)")

seg = (
    fdf.groupby(["City", "Road_traffic_density"])
    .agg(orders=("SLA_Met_dynamic", "size"), sla_pct=("SLA_Met_dynamic", "mean"))
    .reset_index()
)
seg = seg[seg["orders"] >= 30]
seg["sla_pct"] = (seg["sla_pct"] * 100).round(1)
seg = seg.sort_values("sla_pct")

st.dataframe(
    seg.rename(columns={"City": "City Type", "Road_traffic_density": "Traffic",
                         "orders": "Orders", "sla_pct": "SLA Compliance %"}),
    use_container_width=True, hide_index=True,
)

st.caption(
    "Data: Kaggle Food Delivery Dataset (gauravmalik26). SLA defined as delivery within the "
    "selected threshold minutes. Built with Streamlit + Plotly."
)
