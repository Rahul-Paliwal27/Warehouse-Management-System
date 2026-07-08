# 📦 Warehouse Management System

A Python and SQLite-based Warehouse Management System that simulates real-world warehouse operations. The system automatically allocates customer orders to the nearest warehouse based on geographical distance, validates inventory, manages order lifecycle, updates stock levels, and provides warehouse analytics through an interactive command-line interface.

## 📖 Project Overview

The Warehouse Management System (WMS) is designed to automate warehouse operations by managing inventory, customer orders, and warehouse allocation.

When a customer places an order, the system determines the nearest warehouse using the Haversine distance formula, verifies inventory availability, allocates stock, updates inventory, estimates delivery time, and generates a dispatch slip.

The project uses SQLite as the backend database to store warehouse, inventory, orders, and order items, replacing Excel-based storage with a normalized relational database.

## ✨ Features

- 📍 Automatic nearest warehouse selection using Haversine distance
- 📦 Inventory availability validation before order allocation
- 🛒 Multi-item customer order support
- 🗄️ SQLite-based relational database
- 📄 Automatic dispatch slip generation
- 📊 Warehouse analytics dashboard
- 🔄 Order status management (Allocated → Picking → Packed → Dispatched → Delivered)
- 📥 Inventory restocking
- ⚠️ Low stock reporting
- 🚚 Delivery ETA estimation based on warehouse distance


---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application logic |
| SQLite | Database management |
| Geocoder | Customer location detection |
| OpenPyXL | Initial Excel data import |
| Git & GitHub | Version control |

---

## 📂 Project Structure

```text
Warehouse-Management-System/
│
├── data/
│   └── LOCATION-WARE.xlsx
│
├── database/
│   ├── create_database.py
│   ├── seed_database.py
│   └── warehouse.db
│
├── output/
│   └── dispatch_order_list/
│
├── screenshots/
│
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 🗄️ Database Schema

The project uses a normalized SQLite database with four tables.

### warehouse

Stores warehouse location information.

| Column |
|--------|
| warehouse_id |
| city |
| latitude |
| longitude |

### inventory

Stores stock available in each warehouse.

| Column |
|--------|
| warehouse_id |
| item_id |
| item_name |
| category |
| stock |

### orders

Stores order-level information.

| Column |
|--------|
| order_id |
| warehouse_id |
| status |
| order_date |
| expected_date |

### order_items

Stores all items belonging to an order.

| Column |
|--------|
| order_id |
| item |
| quantity |

---

## ⚙️ Workflow

The Warehouse Management System follows the workflow below:

1. Customer places an order.
2. The system detects the customer's location using Geocoder.
3. Distances to all warehouses are calculated using the Haversine formula.
4. The nearest warehouse with sufficient inventory is selected.
5. Inventory is validated and allocated.
6. Stock is updated in the SQLite database.
7. A dispatch slip is generated.
8. Delivery ETA is estimated based on distance.
9. Order status is tracked through different stages.
10. Warehouse dashboard provides analytics and inventory insights.


---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Warehouse-Management-System.git
```

Navigate to the project directory

```bash
cd Warehouse-Management-System
```

Install the required dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

Create the database

```bash
python database/create_database.py
```

Seed the initial warehouse and inventory data

```bash
python database/seed_database.py
```

Run the application

```bash
python main.py
```


---

## 📋 Available Operations

- Place Order
- View Orders
- Update Order Status
- Warehouse Dashboard
- Restock Inventory
- Low Stock Report


---

## 📚 Concepts Demonstrated

- Python Programming
- SQLite Database Design
- CRUD Operations
- Database Normalization
- SQL Aggregation (`COUNT`, `SUM`, `GROUP BY`, `ORDER BY`)
- Inventory Management
- Warehouse Allocation Logic
- Haversine Distance Calculation
- Modular Programming
- Git & GitHub Version Control


---

## 👨‍💻 Author

**Rahul Paliwal**

If you found this project useful, feel free to ⭐ the repository.
