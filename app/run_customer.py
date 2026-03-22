from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core import (
    init_db, Dish, Order, OrderItem, 
    get_db_connection, create_order
)
import sqlite3

app_customer = FastAPI()

app_customer.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app_customer.on_event("startup")
async def startup_event():
    init_db()

@app_customer.get("/dishes")
async def get_dishes():
    conn = sqlite3.connect("data/smartbite.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM dishes")
    dishes = cursor.fetchall()
    conn.close()
    
    return [{"id": d[0], "name": d[1], "description": d[2], "price": d[3]} for d in dishes]

@app_customer.post("/order")
async def place_order(order: Order):
    try:
        order_id = create_order(order.items)
        return {"orderId": order_id, "status": "confirmed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_customer, host="0.0.0.0", port=8000)
