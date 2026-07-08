import sqlite3
import pandas as pd
import os
 
 
conn = sqlite3.connect("database/warehouse.db")
cursor=conn.cursor()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
warehouse_file=os.path.join(BASE_DIR,"data","LOCATION-WARE.xlsx")

loc_df=pd.read_excel(warehouse_file,sheet_name="warehouse_loc")
inv_df=pd.read_excel(warehouse_file,sheet_name="warehouse_inv")
loc_df.columns = loc_df.columns.str.lower()
inv_df.columns = inv_df.columns.str.lower()


for _,row in loc_df.iterrows():
    cursor.execute("""INSERT OR IGNORE INTO  warehouse(warehouse_id, city, latitude, longitude)
                values(?,?,?,?)""",
                (row['id'],row['city'],row['latitude'],row['longitude'])
                )

for _,row in inv_df.iterrows():
    cursor.execute("""INSERT INTO  inventory(warehouse_id, item_id, item_name, category, stock)
                values(?,?,?,?,?)""",
                (row['id'],row['item_id'],row['item_name'],row['category'],row['stock_q'])
                )
    
conn.commit()
conn.close()
print(f"{len(loc_df)} Warehouses Inserted")
print(f"{len(inv_df)} Inventory Records Inserted")
print("seed data sucessfull")