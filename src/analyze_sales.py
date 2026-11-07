"""Summarize menu sales and illustrative contribution."""
from pathlib import Path
import pandas as pd
D=Path(__file__).resolve().parents[1]/"data"
orders=pd.read_csv(D/"orders.csv"); lines=pd.read_csv(D/"order_items.csv"); menu=pd.read_csv(D/"menu.csv")
valid=orders.loc[orders.order_status=="Completed",["order_id","customer_id","order_datetime","order_channel"]]
df=lines.merge(valid,on="order_id",validate="many_to_one").merge(menu[["menu_item_id","item_name","category"]],on="menu_item_id",validate="many_to_one")
df["revenue"]=df.quantity*df.unit_price; df["estimated_cost"]=df.quantity*df.estimated_unit_cost
s=df.groupby(["category","item_name"],as_index=False).agg(units_sold=("quantity","sum"),revenue=("revenue","sum"),estimated_cost=("estimated_cost","sum"))
s["estimated_margin_pct"]=((s.revenue-s.estimated_cost)/s.revenue*100).round(2); s.to_csv(D/"menu_performance.csv",index=False)
print(s.sort_values("revenue",ascending=False).to_string(index=False))
print("Completed orders:",valid.order_id.nunique())
