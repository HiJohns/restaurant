from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.core import (
    init_db, DishCreate, OrderStatusUpdate,
    get_db_connection
)
from pydantic import BaseModel
import sqlite3
import secrets
import hashlib
import os

app_staff = FastAPI()

app_staff.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    role: str

MOCK_USERS = {
    "chef_01": {
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "CHEF"
    },
    "waiter_01": {
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "WAITER"
    },
    "cashier_01": {
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "CASHIER"
    }
}

AUTH_TOKENS = {}

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    if token not in AUTH_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return AUTH_TOKENS[token]

@app_staff.on_event("startup")
async def startup_event():
    init_db()

@app_staff.post("/api/login", response_model=LoginResponse)
async def login(login_req: LoginRequest):
    user = MOCK_USERS.get(login_req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    input_hash = hashlib.sha256(login_req.password.encode()).hexdigest()
    if input_hash != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = secrets.token_urlsafe(32)
    AUTH_TOKENS[token] = {
        "username": login_req.username,
        "role": user["role"]
    }
    
    return {"access_token": token, "role": user["role"]}

@app_staff.get("/api/orders/pending")
async def get_pending_orders(token_data: dict = Depends(verify_token)):
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

@app_staff.patch("/api/order/{order_id}/status")
async def update_order_status(order_id: int, update: OrderStatusUpdate, token_data: dict = Depends(verify_token)):
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

@app_staff.get("/api/analytics/revenue")
async def get_revenue_analytics(token_data: dict = Depends(verify_token)):
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

@app_staff.post("/api/dishes")
async def create_dish(dish: DishCreate, token_data: dict = Depends(verify_token)):
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

@app_staff.delete("/api/dishes/{dish_id}")
async def delete_dish(dish_id: int, token_data: dict = Depends(verify_token)):
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

# Mount static files
app_staff.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Catch-all route for SPA (must be added LAST)
@app_staff.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Catch-all route: Serve index.html for all non-API routes
    This enables client-side routing in React SPA
    """
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_path = os.path.join("frontend/dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=500, detail="Frontend build not found. Run 'cd frontend && npm run build'")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_staff, host="0.0.0.0", port=8001)
