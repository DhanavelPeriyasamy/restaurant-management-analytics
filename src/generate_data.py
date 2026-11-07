"""Generate synthetic restaurant orders, menu, customers and order lines."""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data"; OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(81)
menu=pd.DataFrame([(1,"Chicken Biryani","Main Course",220,105),(2,"Veg Biryani","Main Course",170,78),(3,"Paneer Butter Masala","Main Course",210,92),(4,"Butter Naan","Sides",45,14),(5,"Chicken 65","Starters",160,68),(6,"Fresh Lime Soda","Beverages",65,18),(7,"Gulab Jamun","Dessert",70,22),(8,"Masala Dosa","Breakfast",110,42)],columns=["menu_item_id","item_name","category","unit_price","estimated_unit_cost"])
customers=pd.DataFrame({"customer_id":range(1,701),"customer_segment":rng.choice(["Regular","Occasional","New"],700,p=[.25,.55,.20])})
n=3200; stamps=pd.Timestamp("2025-01-01")+pd.to_timedelta(rng.integers(0,365*24*60,n),unit="m")
orders=pd.DataFrame({"order_id":range(50001,50001+n),"customer_id":rng.integers(1,701,n),"order_datetime":stamps,"order_channel":rng.choice(["Dine-in","Takeaway","Delivery"],n,p=[.48,.27,.25]),"order_status":rng.choice(["Completed","Cancelled"],n,p=[.96,.04])})
lines=[]; iid=1
for o in orders.itertuples(index=False):
 if o.order_status!="Completed": continue
 for mid in rng.choice(menu.menu_item_id,size=int(rng.integers(1,5)),replace=False):
  m=menu.loc[menu.menu_item_id==mid].iloc[0]; q=int(rng.integers(1,4))
  lines.append((iid,o.order_id,int(mid),q,float(m.unit_price),float(m.estimated_unit_cost))); iid+=1
items=pd.DataFrame(lines,columns=["order_item_id","order_id","menu_item_id","quantity","unit_price","estimated_unit_cost"])
for name,df in [("menu",menu),("customers",customers),("orders",orders),("order_items",items)]: df.to_csv(OUT/f"{name}.csv",index=False)
print(f"Generated {len(orders)} orders and {len(items)} order lines")
