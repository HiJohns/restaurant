from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from app.core import (
    init_db, Dish, Order, OrderItem, 
    get_db_connection, create_order
)
from pydantic import BaseModel
import sqlite3
import secrets
import hashlib

app_customer = FastAPI()

app_customer.add_middleware(
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

@app_customer.on_event("startup")
async def startup_event():
    init_db()

@app_customer.post("/api/login", response_model=LoginResponse)
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
    uvicorn.run(app_customer, host="0.0.0.0", port=8001)