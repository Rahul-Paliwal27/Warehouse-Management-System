import sqlite3

conn = sqlite3.connect("database/warehouse.db")
cursor=conn.cursor()

#creating all the tables

cursor.execute("""CREATE TABLE IF NOT EXISTS warehouse(
               warehouse_id TEXT PRIMARY KEY,
               city TEXT,
               latitude REAL,
               longitude REAL 
               )
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS inventory(
               warehouse_id TEXT,
               item_id TEXT,
               item_name TEXT,
               category TEXT,
               stock INTEGER
               )""")
cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
               order_id TEXT PRIMARY KEY,
               warehouse_id TEXT,
               status TEXT,
               order_date DATE,
               expected_date DATE
               )
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS order_items(
               order_id TEXT,
               item TEXT,
               quantity  INTEGER
               )
""")

conn.commit()
conn.close()
print("database created successfully")