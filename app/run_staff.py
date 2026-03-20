from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core import (
    init_db, DishCreate, OrderStatusUpdate,
    get_db_connection
)
import sqlite3

app_staff = FastAPI()

app_staff.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app_staff.on_event("startup")
async def startup_event():
    init_db()

@app_staff.get("/dishes")
async def get_dishes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM dishes")
    dishes = cursor.fetchall()
    conn.close()
    
    return [{"id": d[0], "name": d[1], "description": d[2], "price": d[3]} for d in dishes]

@app_staff.get("/orders/pending")
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

@app_staff.patch("/order/{order_id}/status")
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

@app_staff.get("/analytics/revenue")
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

@app_staff.post("/dishes")
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

@app_staff.delete("/dishes/{dish_id}")
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
    uvicorn.run(app_staff, host="0.0.0.0", port=8000)
