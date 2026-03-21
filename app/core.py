from fastapi import HTTPException
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
