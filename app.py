"""Restaurant revenue and menu intelligence dashboard.

Run with: streamlit run app.py
All restaurant, customer and transaction records are synthetic.
"""
from pathlib import Path
import subprocess
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.set_page_config(page_title="Saffron | Restaurant Intelligence", page_icon="◈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:#F4F0E8;color:#29251F;}
[data-testid="stSidebar"]{background:#25231F;}
[data-testid="stSidebar"] *{color:#F5EFE3 !important;}
[data-testid="stMetric"]{background:#FFFCF5;border:1px solid #E7DDC9;padding:18px;border-radius:5px;box-shadow:0 4px 12px rgba(44,35,22,.05);}
[data-testid="stMetricLabel"]{color:#85765F;}
[data-testid="stMetricValue"]{color:#9B4D25;font-family:'Playfair Display',serif;}
h1,h2,h3{font-family:'Playfair Display',serif;color:#3A3026;}
.block-container{padding-top:2rem;max-width:1450px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    names = ["menu", "customers", "orders", "order_items"]
    paths = {name: DATA_DIR / f"{name}.csv" for name in names}
    if not all(path.exists() for path in paths.values()):
        subprocess.run([sys.executable, str(ROOT / "src" / "generate_data.py")], check=True)
    tables = {name: pd.read_csv(path, parse_dates=["order_datetime"] if name == "orders" else None) for name, path in paths.items()}
    orders, items, menu, customers = tables["orders"], tables["order_items"], tables["menu"], tables["customers"]
    sales = orders.merge(items, on="order_id", how="inner")
    sales = sales.merge(menu[["menu_item_id","item_name","category"]], on="menu_item_id", how="left")
    sales = sales.merge(customers, on="customer_id", how="left")
    sales = sales[sales.order_status.eq("Completed")].copy()
    sales["revenue"] = sales.quantity * sales.unit_price
    sales["food_cost"] = sales.quantity * sales.estimated_unit_cost
    sales["contribution"] = sales.revenue - sales.food_cost
    sales["order_date"] = sales.order_datetime.dt.date
    sales["month"] = sales.order_datetime.dt.to_period("M").astype(str)
    sales["weekday"] = sales.order_datetime.dt.day_name()
    sales["hour"] = sales.order_datetime.dt.hour
    return sales

data = load_data()
st.markdown("<div style='background:#25231F;padding:26px 30px;border-left:7px solid #C47A32;margin-bottom:20px'><div style='font-size:11px;letter-spacing:3px;color:#D9A35D;font-weight:700'>SAFFRON • RESTAURANT BUSINESS INTELLIGENCE</div><div style='font-family:Playfair Display;font-size:34px;font-weight:800;color:#FFF8E9'>The Restaurant Ledger</div><div style='color:#C9BDA8;margin-top:5px'>Sales performance, menu profitability and guest behaviour</div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ◈ SAFFRON")
    st.caption("REVENUE & MENU INTELLIGENCE")
    st.markdown("---")
    date_min, date_max = data.order_datetime.min().date(), data.order_datetime.max().date()
    date_range = st.date_input("Trading period", (date_min, date_max), min_value=date_min, max_value=date_max)
    channels = sorted(data.order_channel.dropna().unique())
    channel_filter = st.multiselect("Sales channel", channels, default=channels)
    categories = sorted(data.category.dropna().unique())
    category_filter = st.multiselect("Menu section", categories, default=categories)
    segments = sorted(data.customer_segment.dropna().unique())
    segment_filter = st.multiselect("Guest segment", segments, default=segments)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
else:
    start, end = pd.Timestamp(date_min), pd.Timestamp(date_max) + pd.Timedelta(days=1)
view = data[data.order_datetime.between(start, end, inclusive="left") & data.order_channel.isin(channel_filter) & data.category.isin(category_filter) & data.customer_segment.isin(segment_filter)].copy()

if view.empty:
    st.warning("No completed sales match these filters.")
    st.stop()

order_totals = view.groupby("order_id", as_index=False).agg(order_value=("revenue","sum"), customer_id=("customer_id","first"))
revenue = view.revenue.sum()
order_count = order_totals.order_id.nunique()
aov = order_totals.order_value.mean()
guest_count = view.customer_id.nunique()
contribution = view.contribution.sum()
margin = contribution / revenue * 100 if revenue else 0

kpi = st.columns(4)
kpi[0].metric("Net item sales", f"₹{revenue:,.0f}")
kpi[1].metric("Completed orders", f"{order_count:,}")
kpi[2].metric("Average bill value", f"₹{aov:,.0f}")
kpi[3].metric("Estimated food margin", f"{margin:.1f}%")

st.markdown("### The sales story")
left, right = st.columns([1.35, 1])
with left:
    monthly = view.groupby("month", as_index=False).agg(Sales=("revenue","sum"))
    fig = px.area(monthly, x="month", y="Sales", color_discrete_sequence=["#B85F2A"])
    fig.update_traces(line=dict(width=3), fillcolor="rgba(184,95,42,.18)")
    fig.update_layout(title="Monthly sales rhythm", paper_bgcolor="#FFFCF5", plot_bgcolor="#FFFCF5", font_color="#4A3B2A", xaxis_title="", yaxis_title="Sales (₹)", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    category_sales = view.groupby("category", as_index=False).agg(Sales=("revenue","sum"))
    fig = px.treemap(category_sales, path=["category"], values="Sales", color="Sales", color_continuous_scale=["#F2D9B4","#A64F25"])
    fig.update_layout(title="Menu section contribution", paper_bgcolor="#FFFCF5", font_color="#4A3B2A", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Menu engineering")
left, right = st.columns([1.25, 1])
with left:
    item = view.groupby("item_name", as_index=False).agg(Units=("quantity","sum"), Sales=("revenue","sum"), Contribution=("contribution","sum"))
    fig = px.scatter(item, x="Units", y="Contribution", size="Sales", color="Sales", hover_name="item_name", color_continuous_scale=["#EBCB91","#A64F25"], labels={"Units":"Units sold","Contribution":"Estimated contribution (₹)"})
    fig.update_layout(title="Menu stars: volume vs contribution", paper_bgcolor="#FFFCF5", plot_bgcolor="#FFFCF5", font_color="#4A3B2A", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    channel = view.groupby("order_channel", as_index=False).agg(Sales=("revenue","sum"))
    fig = px.pie(channel, names="order_channel", values="Sales", hole=.62, color_discrete_sequence=["#A64F25","#D69A4A","#4D6651"])
    fig.update_layout(title="Where revenue comes from", paper_bgcolor="#FFFCF5", font_color="#4A3B2A", margin=dict(l=10,r=10,t=55,b=10), legend_title="Channel")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Guest demand patterns")
left, right = st.columns([1.2, 1])
with left:
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    demand = view.pivot_table(index="weekday", columns="hour", values="order_id", aggfunc="nunique", fill_value=0).reindex(day_order)
    fig = px.imshow(demand, aspect="auto", color_continuous_scale=["#F8EEDC","#C47A32","#542D20"], labels={"x":"Hour of day","y":"Day of week","color":"Orders"})
    fig.update_layout(title="Peak ordering heatmap", paper_bgcolor="#FFFCF5", font_color="#4A3B2A", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    guests = view.groupby("customer_id", as_index=False).agg(Orders=("order_id","nunique"), Sales=("revenue","sum"), Segment=("customer_segment","first"))
    fig = px.box(guests, x="Segment", y="Sales", color="Segment", color_discrete_sequence=["#A64F25","#D69A4A","#4D6651"], points="outliers")
    fig.update_layout(title="Guest spend by segment", paper_bgcolor="#FFFCF5", plot_bgcolor="#FFFCF5", font_color="#4A3B2A", showlegend=False, xaxis_title="", yaxis_title="Sales per guest (₹)", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Menu performance register")
detail = view.groupby(["item_name","category"], as_index=False).agg(Units_sold=("quantity","sum"), Sales=("revenue","sum"), Estimated_cost=("food_cost","sum"), Contribution=("contribution","sum"))
detail["Estimated_margin_pct"] = (detail.Contribution / detail.Sales * 100).round(1)
st.dataframe(detail.sort_values("Sales", ascending=False).rename(columns={"item_name":"Menu item","category":"Section","Units_sold":"Units sold","Sales":"Sales (₹)","Estimated_cost":"Estimated cost (₹)","Contribution":"Contribution (₹)","Estimated_margin_pct":"Est. margin (%)"}), use_container_width=True, hide_index=True)
st.download_button("Export filtered sales detail", view.to_csv(index=False).encode("utf-8"), "restaurant_sales_detail.csv", "text/csv")

with st.expander("Financial definitions and assumptions"):
    st.write("All transactions and guests are fictional. Sales are calculated from completed order lines. Estimated food margin subtracts synthetic ingredient-cost assumptions only; it is not audited profit and excludes labour, rent, tax, waste, discounts and delivery commissions.")
st.caption("SAFFRON • Synthetic portfolio transactions • Built with Python, Streamlit and Plotly")
