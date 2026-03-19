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
            status TEXT NOT NULL
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
    
    # Insert sample dishes if table is empty
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

class OrderItem(BaseModel):
    id: int
    quantity: int

class Order(BaseModel):
    items: List[OrderItem]

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

def create_order(order_items: List[OrderItem]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO orders (status) VALUES (?)", ("confirmed",))
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
