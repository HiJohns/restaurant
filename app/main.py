from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import os

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "smartbite.db")

# Initialize database if it doesn't exist
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL DEFAULT 0.0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            dish_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (dish_id) REFERENCES dishes (id)
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM dishes")
    if cursor.fetchone()[0] == 0:
        sample_dishes = [
            (1, "Margherita Pizza", "Classic pizza with tomato, mozzarella, and basil", 12.99),
            (2, "Caesar Salad", "Fresh romaine lettuce with parmesan and croutons", 8.99),
            (3, "Spaghetti Carbonara", "Pasta with eggs, bacon, and parmesan", 14.99),
            (4, "Tiramisu", "Classic Italian dessert with coffee and mascarpone", 6.99),
        ]
        cursor.executemany("INSERT INTO dishes VALUES (?, ?, ?, ?)", sample_dishes)
    
    conn.commit()
    conn.close()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://opencode.linxdeep.com:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Dish(BaseModel):
    id: int
    name: str
    description: str
    price: float

class DishCreate(BaseModel):
    name: str
    description: str
    price: float

class OrderItem(BaseModel):
    id: int
    quantity: int

class Order(BaseModel):
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    status: str

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/dishes")
async def get_dishes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM dishes")
    dishes = cursor.fetchall()
    conn.close()
    
    return [{"id": d[0], "name": d[1], "description": d[2], "price": d[3]} for d in dishes]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_order_total(conn, order_items: List[OrderItem]) -> float:
    cursor = conn.cursor()
    total = 0.0
    for item in order_items:
        cursor.execute("SELECT price FROM dishes WHERE id = ?", (item.id,))
        row = cursor.fetchone()
        if row:
            total += row["price"] * item.quantity
    return total

def create_order(order_items: List[OrderItem]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        total = calculate_order_total(conn, order_items)
        cursor.execute(
            "INSERT INTO orders (status, total_amount) VALUES (?, ?)",
            ("confirmed", total)
        )
        order_id = cursor.lastrowid
        
        if order_id is None:
            raise Exception("Failed to create order")
        
        for item in order_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, dish_id, quantity) VALUES (?, ?, ?)",
                (order_id, item.id, item.quantity)
            )
        
        conn.commit()
        return order_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@app.post("/order")
async def place_order(order: Order):
    try:
        order_id = create_order(order.items)
        return {"orderId": order_id, "status": "confirmed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/pending")
async def get_pending_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, o.status, o.created_at, o.total_amount,
               GROUP_CONCAT(d.name || ' x' || oi.quantity) as items
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN dishes d ON oi.dish_id = d.id
        WHERE o.status IN ('confirmed', 'COOKING')
        GROUP BY o.id
        ORDER BY o.created_at ASC
    """)
    orders = cursor.fetchall()
    conn.close()
    return [dict(row) for row in orders]

@app.patch("/order/{order_id}/status")
async def update_order_status(order_id: int, update: OrderStatusUpdate):
    valid_statuses = ["confirmed", "COOKING", "READY", "SERVED", "PAID"]
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, status FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
    
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (update.status, order_id))
    conn.commit()
    conn.close()
    
    return {"orderId": order_id, "status": update.status}

@app.get("/analytics/revenue")
async def get_revenue_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) as total_revenue, COUNT(*) as total_orders
        FROM orders WHERE status = 'PAID'
    """)
    revenue_stats = dict(cursor.fetchone())
    
    cursor.execute("""
        SELECT d.name, SUM(oi.quantity) as total_ordered, SUM(d.price * oi.quantity) as revenue
        FROM order_items oi
        JOIN dishes d ON oi.dish_id = d.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'PAID'
        GROUP BY d.id, d.name
        ORDER BY total_ordered DESC
    """)
    dish_stats = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "summary": revenue_stats,
        "by_dish": dish_stats
    }

@app.post("/dishes")
async def create_dish(dish: DishCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dishes (name, description, price) VALUES (?, ?, ?)",
        (dish.name, dish.description, dish.price)
    )
    dish_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": dish_id, "name": dish.name, "description": dish.description, "price": dish.price}

@app.delete("/dishes/{dish_id}")
async def delete_dish(dish_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM dishes WHERE id = ?", (dish_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Dish not found")
    
    cursor.execute("DELETE FROM order_items WHERE dish_id = ?", (dish_id,))
    cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
    conn.commit()
    conn.close()
    
    return {"message": f"Dish {dish_id} deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
