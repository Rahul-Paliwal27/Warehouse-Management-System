import os
import math
import geocoder
from datetime import datetime,timedelta
import sqlite3
conn = sqlite3.connect("database/warehouse.db")
conn.row_factory = sqlite3.Row
cursor=conn.cursor()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder=os.path.join(BASE_DIR,"output","dispatch_order_list")



def place_order():

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
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # warehouse_file=os.path.join(BASE_DIR,"data","LOCATION-WARE.xlsx")
    
    # loc_df=pd.read_excel(warehouse_file,sheet_name="warehouse_loc")
    # inv_df=pd.read_excel(warehouse_file,sheet_name="warehouse_inv")

    cursor.execute("""SELECT * FROM warehouse""")
    warehouse_data=cursor.fetchall()#its a list of tuple

    # cursor.execute("""SELECT *FROM INVENTORY""")
    # warehouse_inv=cursor.fetchall()

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
        # orders_path=os.path.join("output","order_data.xlsx")
        cursor.execute("""SELECT order_id  FROM orders ORDER BY  order_id DESC LIMIT 1""")
        result= cursor.fetchone()
        if result is None:
            return "ORD0001"
        
        last_id = result["order_id"]

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
            customer_location
            ):
        distances=[]
        for warehouse in warehouse_data:
            warehouse_lat=warehouse["latitude"]
            warehouse_lon=warehouse["longitude"]
            
            distance= haversine(
                customer_location["latitude"],
                warehouse_lat,
                customer_location["longitude"],
                warehouse_lon
            )

            distances.append(
                {"id":warehouse["warehouse_id"],"city":warehouse["city"],"distances":distance,"lat":warehouse_lat,"lon":warehouse_lon}
            )

        sorted_dis=sorted(distances,key=lambda x: x["distances"]) ##sorted distance warehosue  is stored in the variable
        return sorted_dis


    # now Checking the nearest warehouse and the inventory with it
    def check_inv(
            customer_order,
            sorted_dis
            ):
        for warehouse in sorted_dis:
            warehouse_id=warehouse['id']
            cursor.execute("""SELECT * FROM inventory WHERE warehouse_id=?""",(warehouse_id,))
            warehouse_inv=cursor.fetchall()

            available=True
            for item,quantity in zip(customer_order['item'],customer_order['quantity']):
                item=item.lower()
                product_needed=None
                for product in warehouse_inv:
                    if product["item_name"].lower()==item:
                        product_needed = product
                if product_needed is None:
                    available=False
                    print("item not available right now")
                    break
                stock=product_needed["stock"]

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
            customer_order
            ):
       
        for item,quantity in zip(customer_order['item'],customer_order['quantity']):
            item=item.lower()
            cursor.execute(""" SELECT stock FROM inventory WHERE warehouse_id=? AND lower(item_name)=? """,(warehouse_id,item.lower()))
            result= cursor.fetchone()
            stock=result["stock"]
            new_stock = stock-quantity
            cursor.execute(""" UPDATE inventory SET stock=?  WHERE warehouse_id=? AND lower(item_name)=? """,(new_stock,warehouse_id,item.lower()))
            print(f"{item} updated to {new_stock}")
        conn.commit()

        
            # print(warehouse_inv.head())




    def order_storing(
            order_id,
            warehouse_id,
            order_date,
            delivery_date
            ):
        status="Allocated"
        
        cursor.execute("""INSERT INTO orders (order_id,warehouse_id,status,order_date,expected_date) VALUES (?,?,?,?,?)""",(order_id,warehouse_id,status,order_date,delivery_date) )

        for item,quantity in zip(customer_order["item"],customer_order["quantity"]):
            cursor.execute(""" INSERT INTO order_items(order_id,item,quantity) VALUES (?,?,?)""",(order_id,item,quantity))
        conn.commit()

    def delivery_ETA(distance):
        if distance<=50:
            return 0
        elif distance<=200:
            return 1
        elif distance<=500:
            return 2
        else:
            return 3
        

    # def order_status(order_id,new_status):
    #     if order_id not in orders_df["order_id"].values:
    #         print("order not found")
    #         return
    #     cursor.execute("""UPDATE orders SET status=? WHERE order_id=?""",(new_status,order_id))
    #     orders_df= pd.read_excel(orders_path)
    #     print(f"{order_id} updates to {new_status}")




    # main program 
    order_id= generate_order_id()
    customer_order=get_customer_order()
    sorted_dis=nearest_warehouse_loc(customer_location)
    selected_warehouse=check_inv(customer_order,sorted_dis)
    if selected_warehouse is None:
        print("no warehouse available")
        exit()

    warehouse_id=selected_warehouse['id']
    

    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # folder=os.path.join(BASE_DIR,"output","dispatch_order_list")
    os.makedirs(folder, exist_ok=True)
    # "C:\Users\HP\Downloads\order_data.xlsx"

    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # orders_path=os.path.join(BASE_DIR,"output","order_data.xlsx")
    distance = selected_warehouse['distances']
    days = delivery_ETA(distance)

    delivery_date=order_date+timedelta(days=days)

    if warehouse_id:
        update_inventory(warehouse_id,customer_order)
        order_storing(order_id,warehouse_id,order_date,delivery_date)
        generate_dispatch_slip(folder,order_id,selected_warehouse,customer_order,delivery_date,order_date)


def view_order():
        cursor.execute(""" SELECT * FROM orders""")
        orders=cursor.fetchall()
        for order in orders:
        
            print("="*40)

            print(f"Order ID   : {order['order_id']}")

            print(f"Warehouse  : {order['warehouse_id']}")


            print(f"Status     : {order['status']}")

            print(f"Order Date : {order['order_date']}")

            print(f"ETA        : {order['expected_date']}")

            print("\nItems")
            cursor.execute("""SELECT * FROM order_items WHERE order_id=?""",(order["order_id"],))
            items= cursor.fetchall()
            for item in items:
                print(f"{item['item']} * {item['quantity']}")      

def order_status():
    order_id=input("Enter Order ID: ").upper()
    cursor.execute(""" SELECT status FROM orders WHERE order_id=?""",(order_id,))
    order=cursor.fetchone()
    if order is None:
        print("order not found")
        return
    print("===STATUS MENU===")
    status_map={"1":"Picking","2":"Packed","3":"Dispatching","4":"Delivered"}
    for key,values in status_map.items():
        print(key,values)
    choice=input("enter the choice: ")
    new_status=status_map[choice]
    cursor.execute("""UPDATE  orders SET status=? WHERE order_id=?""",(new_status,order_id))
    conn.commit()
    print("status updated sucessfully")
    




def warehouse_dashboard():
    cursor.execute("SELECT order_id, status FROM orders")
    for row in cursor.fetchall():
        print(dict(row))
        
    cursor.execute(""" SELECT COUNT(DISTINCT order_id) FROM orders""")
    result=cursor.fetchone()

    cursor.execute(""" SELECT status, COUNT(*) AS total FROM orders GROUP BY status""")
    status_data=cursor.fetchall()

    status_count = {}

    for row in status_data:
        status_count[row["status"]] = row["total"]



    allocated=status_count.get("Allocated",0)
    picking=status_count.get("Picking",0)
    packed = status_count.get("Packed",0)
    dispatched = status_count.get("Dispatching",0)
    delivered = status_count.get("Delivered",0)
    
    print("="*10)
    print("WAREHOUSE DASHBOARD")
    print("="*10)
    print(f"Total Orders : {result[0]}")
    print(f"Allocated    : {allocated}")
    print(f"Picking      : {picking}")
    print(f"Packed       : {packed}")
    print(f"Dispatched   : {dispatched}")
    print(f"Delivered    : {delivered}")

    cursor.execute("""SELECT item,SUM(quantity) AS total_quantity FROM order_items GROUP BY item ORDER BY total_quantity DESC LIMIT 1;""")
    result = cursor.fetchone()
    print(f"most ordered item: {result['item']}(qty: {result['total_quantity']})")

    cursor.execute("""SELECT warehouse_id, COUNT(*) AS total_orders FROM orders GROUP BY warehouse_id ORDER BY total_orders DESC LIMIT 1;""")
    result=cursor.fetchone()
    
    print(f"most active warehouse: {result['warehouse_id']}")
    return




def main_menu():
    while True:
        print("\n========= MY SMART WAREHOUSE ========= ")
        print("1.Place order")
        print("2.View order")
        print("3.Update status")
        print("4.warehouse dashboard")
        print("other for exit\n")
        choice=int(input("Enter the choice: "))
        if choice==1:
            place_order()
        elif choice==2:
            view_order()
        elif choice==3:
            order_status()
        elif choice==4:
            warehouse_dashboard()
        else:
            return "Thank you for exit"

main_menu()