import os
import math
import pandas as pd
import geocoder 
from datetime import datetime,timedelta

order_date=datetime.now().date()

g=geocoder.ip('me')
print(g.latlng)
if g.latlng is None:
    print("unable to trace the location")

# customer  location based on the geocoder
customer_location={
    "latitude":g.latlng[0],
     "longitude":g.latlng[1]}
print(customer_location)

# now reading the warehouse loctaions and the inv from the excel 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
warehouse_file=os.path.join(BASE_DIR,"data","LOCATION-WARE.xlsx")
loc_df=pd.read_excel(warehouse_file,sheet_name="warehouse_loc")
inv_df=pd.read_excel(warehouse_file,sheet_name="warehouse_inv")

# taking the order from the cutomer waht he needs and appending it to the custome_order 
def get_customer_order():
    customer_order = {
    "item":[],"quantity":[]
    }
    while True:
        item = input("Enter the item: ")
        quantity = int(input("Enter quantity: "))

        customer_order["item"].append(item)
        customer_order["quantity"].append(quantity)

        if input("Add more? (y/n): ").lower() == "n":
            break
    return customer_order

def generate_order_id():
    orders_path=os.path.join("output","order_data.xlsx")

    if not os.path.exists(orders_path):
        return "ORD0001"
    orders=pd.read_excel(orders_path)
    if orders.empty:
        return "ORD0001"
    last_id = orders.iloc[-1]["order_id"]
    number = int(last_id.replace("ORD",""))
    return f"ORD{number+1:04d}"



# harvesine distance calculation to make the sortest distance possible 
def haversine(
        lat1,
        lat2,
        lon1,
        lon2
        ):
    R= 6371.0
    phi1=math.radians(lat1)
    phi2=math.radians(lat2)
    delta_phi=math.radians(lat2-lat1)
    delta_lamda=math.radians(lon2-lon1)
    a=math.sin(delta_phi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(delta_lamda/2)**2
    c= 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return R*c


# nearest warehouse
def nearest_warehouse_loc(
        customer_location,
        loc_df
        ):
    distances=[]
    for _,rows in loc_df.iterrows():
        warehouse_lat=rows['LATITUDE']
        warehouse_lon=rows['LONGITUDE']
        
        distance= haversine(
            customer_location["latitude"],
            warehouse_lat,
            customer_location["longitude"],
            warehouse_lon
        )

        distances.append(
            {"id":rows['ID'],"city":rows['CITY'],"distances":distance,"lat":warehouse_lat,"lon":warehouse_lon}
        )

    sorted_dis=sorted(distances,key=lambda x: x["distances"]) ##sorted distance warehosue  is stored in the variable
    return sorted_dis


# now Checking the nearest warehouse and the inventory with it
def check_inv(
        customer_order,
        sorted_dis,
        inv_df
        ):
    for warehouse in sorted_dis:
        warehouse_id=warehouse['id']
        warehouse_inv=inv_df[inv_df["ID"] == warehouse_id]

        available=True
        for item,quantity in zip(customer_order['item'],customer_order['quantity']):
            item=item.lower()
            product_needed=warehouse_inv[warehouse_inv['ITEM_NAME'].str.lower()==item]
            if product_needed.empty:
                available=False
                print("item not available right now")
                break
            stock=product_needed['STOCK_Q'].iloc[0]

            if stock<quantity:
                available=False
                break

        if available:
            return warehouse
        
    return None


def generate_dispatch_slip(
        folder,order_id,
        selected_warehouse,
        customer_order,
        delivery_date,
        order_date
        ):
    filename= f"Dispatch_{order_id}.txt"
    filepath=os.path.join(folder,filename)
    with open(filepath,"w") as file:
        file.write("=====DISPATCH SLIP=====\n\n")
        file.write(f"ORDER ID          : {order_id}\n")
        file.write(f"WAREHOUSE ID      : {selected_warehouse['id']}\n")
        file.write(f"CITY              : {selected_warehouse['city']}\n\n")
        file.write("ITEMS:\n")
        for item,quantity in zip(customer_order['item'],customer_order['quantity']):
            file.write(f"-{item} : {quantity}\n")

        file.write(f"order_date        :{order_date}\n") 
        file.write(f"delivery_date     :{delivery_date}\n")
        file.write("="*20)
    print(f"Dispatch list saved at :\n{filepath}")


# updating the inventory
def update_inventory(
        warehouse_id,
        customer_order,
        inv_df
        ):
    warehouse_inv = inv_df[inv_df["ID"] == warehouse_id]
    for item,quantity in zip(customer_order['item'],customer_order['quantity']):
        item=item.lower()
        product_needed=warehouse_inv[warehouse_inv['ITEM_NAME'].str.lower()==item]
        new_stock=product_needed['STOCK_Q'].iloc[0]-quantity
        print(f"{new_stock}: this is the new stock")
        inv_df.loc[(inv_df['ID']==warehouse_id) & (inv_df['ITEM_NAME'].str.lower()==item),'STOCK_Q']=new_stock
        print("new stock with updated warehosue")
        warehouse_inv = inv_df[inv_df["ID"] == warehouse_id]
        # print(warehouse_inv.head())




def order_storing(
        order_id,
        warehouse_id,
        orders_path,
        warehouse_city,
        order_date,
        delivery_date
        ):
    

    for item,quantity in zip(customer_order["item"],customer_order["quantity"]):
        order_data.append({"order_id":order_id,"warehouse_id":warehouse_id,"city":warehouse_city,"item":item,"quantity":quantity,"status":"allocated","order_date":order_date,"expected_date":delivery_date})
    print(order_data)
    orders_df=pd.DataFrame(order_data)

    if os.path.exists(orders_path):
         old_orders=pd.read_excel(orders_path)
         orders_df=pd.concat([old_orders,orders_df],ignore_index=True)
         
    orders_df.to_excel(orders_path,index=False)


def delivery_ETA(distance):
    if distance<=50:
        return 0
    elif distance<=200:
        return 1
    elif distance<=500:
        return 2
    else:
        return 3
    
# main program 
order_id= generate_order_id()
customer_order=get_customer_order()
sorted_dis=nearest_warehouse_loc(customer_location,loc_df)
selected_warehouse=check_inv(customer_order,sorted_dis,inv_df)
if selected_warehouse is None:
    print("no warehouse available")
    exit()

warehouse_id=selected_warehouse['id']
warehouse_city=selected_warehouse['city']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder=os.path.join(BASE_DIR,"output","dispatch_order_list")
os.makedirs(folder, exist_ok=True)
# "C:\Users\HP\Downloads\order_data.xlsx"

order_data=[]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
orders_path=os.path.join(BASE_DIR,"output","order_data.xlsx")
distance = selected_warehouse['distances']
days = delivery_ETA(distance)

delivery_date=order_date+timedelta(days=days)

if warehouse_id:
    update_inventory(warehouse_id,customer_order,inv_df)
    order_storing(order_id,warehouse_id,orders_path,warehouse_city,order_date,delivery_date)
    generate_dispatch_slip(folder,order_id,selected_warehouse,customer_order,delivery_date,order_date)
