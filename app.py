"""Restaurant management dashboard | MySQL companion web view."""
from pathlib import Path
import subprocess
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"
st.set_page_config(page_title="Restaurant Management | Dhanavel Periyasamy",page_icon="◈",layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif;}
.stApp{background:#F8F7F4;color:#292D2B;}
.block-container{max-width:1500px;padding-top:2rem;padding-bottom:3rem;}
[data-testid="stMetric"]{background:#FFFFFF;border:1px solid #E9E5DC;border-radius:12px;padding:17px 18px;box-shadow:0 2px 8px rgba(46,43,34,.035);}
[data-testid="stMetricLabel"]{color:#77776C;font-size:13px;}
[data-testid="stMetricValue"]{color:#405A4A;font-weight:750;}
h1,h2,h3{color:#354B3D;letter-spacing:-.025em;}
div[data-testid="stMultiSelect"] label,div[data-testid="stDateInput"] label{font-weight:650;color:#666A60;}
div[data-testid="stPlotlyChart"]{background:#FFFFFF;border:1px solid #EAE7E0;border-radius:12px;padding:8px;}
hr{border-color:#EAE7E0;}
</style>
""",unsafe_allow_html=True)

@st.cache_data
def load_data():
    names=["menu","customers","orders","order_items"]
    paths={n:DATA/f"{n}.csv" for n in names}
    if not all(p.exists() for p in paths.values()):
        subprocess.run([sys.executable,str(ROOT/"src"/"generate_data.py")],check=True)
    tables={n:pd.read_csv(p,parse_dates=["order_datetime"] if n=="orders" else None) for n,p in paths.items()}
    sales=tables["orders"].merge(tables["order_items"],on="order_id",how="inner")
    sales=sales.merge(tables["menu"][["menu_item_id","item_name","category"]],on="menu_item_id",how="left")
    sales=sales.merge(tables["customers"],on="customer_id",how="left")
    sales=sales[sales.order_status.eq("Completed")].copy()
    sales["revenue"]=sales.quantity*sales.unit_price
    sales["food_cost"]=sales.quantity*sales.estimated_unit_cost
    sales["contribution"]=sales.revenue-sales.food_cost
    sales["month"]=sales.order_datetime.dt.to_period("M").astype(str)
    sales["weekday"]=sales.order_datetime.dt.day_name()
    sales["hour"]=sales.order_datetime.dt.hour
    return sales

df=load_data()
st.markdown("""
<div style="background:#354B3D;border-radius:16px;padding:27px 30px;color:white;margin-bottom:20px">
<div style="font-size:11px;letter-spacing:2px;font-weight:700;color:#E6C58A">RESTAURANT OPERATIONS • MYSQL ANALYTICS</div>
<div style="font-size:31px;font-weight:800;letter-spacing:-1px;color:#FFFFFF;margin-top:5px">Restaurant Performance Dashboard</div>
<div style="font-size:14px;color:#E5E9E2;margin-top:7px">Sales, menu mix, order channels and guest demand in one operating view</div>
</div>
""",unsafe_allow_html=True)

st.markdown("**REPORT FILTERS**")
date_min,date_max=df.order_datetime.min().date(),df.order_datetime.max().date()
f1,f2,f3,f4=st.columns([1.35,1.15,1.2,1.15])
date_range=f1.date_input("Trading date",(date_min,date_max),min_value=date_min,max_value=date_max)
channels=sorted(df.order_channel.dropna().unique())
channel_filter=f2.multiselect("Order channel",channels,default=channels,placeholder="All channels")
categories=sorted(df.category.dropna().unique())
category_filter=f3.multiselect("Menu category",categories,default=categories,placeholder="All categories")
segments=sorted(df.customer_segment.dropna().unique())
segment_filter=f4.multiselect("Guest segment",segments,default=segments,placeholder="All segments")
if isinstance(date_range,(tuple,list)) and len(date_range)==2:
    start,end=pd.Timestamp(date_range[0]),pd.Timestamp(date_range[1])+pd.Timedelta(days=1)
else:
    start,end=pd.Timestamp(date_min),pd.Timestamp(date_max)+pd.Timedelta(days=1)
view=df[df.order_datetime.between(start,end,inclusive="left")&df.order_channel.isin(channel_filter)&df.category.isin(category_filter)&df.customer_segment.isin(segment_filter)].copy()
st.divider()
if view.empty:
    st.info("No completed sales match the selected filters. Expand the date range or categories.")
    st.stop()

orders=view.groupby("order_id",as_index=False).agg(Order_value=("revenue","sum"))
revenue=view.revenue.sum()
order_count=orders.order_id.nunique()
aov=orders.Order_value.mean()
guest_count=view.customer_id.nunique()
margin=view.contribution.sum()/revenue*100 if revenue else 0
st.markdown("### Business overview")
k=st.columns(5)
k[0].metric("Net item sales",f"₹{revenue:,.0f}")
k[1].metric("Completed orders",f"{order_count:,}")
k[2].metric("Average order value",f"₹{aov:,.0f}")
k[3].metric("Unique guests",f"{guest_count:,}")
k[4].metric("Estimated food margin",f"{margin:.1f}%")
st.caption("Food margin uses synthetic ingredient-cost assumptions only; it is not audited restaurant profit.")
st.markdown("### Sales performance")
left,right=st.columns([1.5,1])
with left:
    trend=view.groupby("month",as_index=False).agg(Sales=("revenue","sum"))
    fig=px.line(trend,x="month",y="Sales",markers=True,title="Monthly sales trend",color_discrete_sequence=["#47745A"])
    fig.update_traces(line_width=3,marker_size=6,fill="tozeroy",fillcolor="rgba(71,116,90,.10)")
    fig.update_layout(template="plotly_white",height=340,margin=dict(l=18,r=18,t=55,b=15),xaxis_title="",yaxis_title="Sales (₹)",font_color="#46564B")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    channel=view.groupby("order_channel",as_index=False).agg(Sales=("revenue","sum"))
    fig=px.pie(channel,names="order_channel",values="Sales",hole=.58,title="Sales by order channel",color_discrete_sequence=["#47745A","#D3A85E","#8FA59A"])
    fig.update_layout(template="plotly_white",height=340,margin=dict(l=18,r=18,t=55,b=15),font_color="#46564B",legend_title="")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.markdown("### Menu performance")
left,right=st.columns([1.15,1])
with left:
    cat=view.groupby("category",as_index=False).agg(Sales=("revenue","sum")).sort_values("Sales")
    fig=px.bar(cat,x="Sales",y="category",orientation="h",text_auto=".2s",title="Sales by menu category",color_discrete_sequence=["#47745A"])
    fig.update_layout(template="plotly_white",height=340,margin=dict(l=18,r=18,t=55,b=15),xaxis_title="Sales (₹)",yaxis_title="",font_color="#46564B")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    items=view.groupby(["item_name","category"],as_index=False).agg(Units=("quantity","sum"),Sales=("revenue","sum"),Contribution=("contribution","sum"))
    fig=px.scatter(items,x="Units",y="Contribution",size="Sales",color="category",hover_name="item_name",title="Menu item volume vs contribution",labels={"Units":"Units sold","Contribution":"Estimated contribution (₹)"},color_discrete_sequence=["#47745A","#D3A85E","#8FA59A","#8B7760","#6B7F91"])
    fig.update_layout(template="plotly_white",height=340,margin=dict(l=18,r=18,t=55,b=15),font_color="#46564B",legend_title="Category")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.markdown("### Guest demand patterns")
left,right=st.columns([1.15,1])
with left:
    day_order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heat=view.pivot_table(index="weekday",columns="hour",values="order_id",aggfunc="nunique",fill_value=0).reindex(day_order)
    fig=px.imshow(heat,aspect="auto",color_continuous_scale=["#F2F0E9","#AFC3B3","#47745A"],title="Order activity by weekday and hour",labels={"x":"Hour of day","y":"Weekday","color":"Orders"})
    fig.update_layout(template="plotly_white",height=330,margin=dict(l=18,r=18,t=55,b=15),font_color="#46564B")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    guest=view.groupby("customer_id",as_index=False).agg(Spend=("revenue","sum"),Segment=("customer_segment","first"))
    fig=px.box(guest,x="Segment",y="Spend",color="Segment",points="outliers",title="Guest spend distribution",color_discrete_sequence=["#47745A","#D3A85E","#8FA59A"])
    fig.update_layout(template="plotly_white",height=330,margin=dict(l=18,r=18,t=55,b=15),font_color="#46564B",showlegend=False,xaxis_title="",yaxis_title="Spend per guest (₹)")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.markdown("### Menu item register")
detail=view.groupby(["item_name","category"],as_index=False).agg(Units_sold=("quantity","sum"),Sales=("revenue","sum"),Estimated_cost=("food_cost","sum"),Contribution=("contribution","sum"))
detail["Estimated_margin_pct"]=(detail.Contribution/detail.Sales*100).round(1)
detail=detail.sort_values("Sales",ascending=False).rename(columns={"item_name":"Menu item","category":"Category","Units_sold":"Units sold","Sales":"Sales (₹)","Estimated_cost":"Estimated cost (₹)","Contribution":"Contribution (₹)","Estimated_margin_pct":"Est. margin (%)"})
st.dataframe(detail,use_container_width=True,hide_index=True)
st.download_button("Download filtered sales detail",view.to_csv(index=False).encode("utf-8"),"restaurant_sales_detail.csv","text/csv")
with st.expander("Metric definitions and financial assumptions"):
    st.write("All transactions and customer records are synthetic. Revenue is calculated at order-item grain for completed orders only. Average order value is calculated after aggregating line items to order level. Estimated food margin subtracts synthetic ingredient costs only and excludes labour, rent, tax, waste, discounts and delivery commissions.")
st.caption("Restaurant Management Database • MySQL portfolio project with an interactive Streamlit companion • Synthetic demonstration data")
