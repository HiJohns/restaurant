from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel

app = FastAPI()

class Order(BaseModel):
    customer_id: int
    total_amount: float
    status: str = "PENDING"

def get_db_conn():
    conn = sqlite3.connect('smartbite.db')
    conn.row_factory = sqlite3.Row
    return conn

# 1. CREATE - 顾客订菜
@app.post("/order")
def create_order(order: Order):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)",
                   (order.customer_id, order.total_amount, order.status))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return {"message": "订单已创建", "order_id": order_id}

# 2. READ - 厨师/服务员查看订单
@app.get("/order/{order_id}")
def read_order(order_id: int):
    conn = get_db_conn()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    conn.close()
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    return dict(order)

# 3. UPDATE - 厨师改变状态 (PENDING -> COOKING)
@app.put("/order/{order_id}")
def update_order_status(order_id: int, status: str):
    conn = get_db_conn()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()
    return {"message": f"订单 {order_id} 状态已更新为 {status}"}

# 4. DELETE - 店主/IT 管理员删除订单
@app.delete("/order/{order_id}")
def delete_order(order_id: int):
    conn = get_db_conn()
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return {"message": "订单已删除"}
