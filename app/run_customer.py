from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
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

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

@app_customer.on_event("startup")
async def startup_event():
    init_db()

@api_router.get("/dishes")
async def get_dishes():
    conn = sqlite3.connect("data/smartbite.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM dishes")
    dishes = cursor.fetchall()
    conn.close()
    
    return [{"id": d[0], "name": d[1], "description": d[2], "price": d[3]} for d in dishes]

@api_router.post("/order")
async def place_order(order: Order):
    try:
        order_id = create_order(order.items)
        return {"orderId": order_id, "status": "confirmed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include API router
app_customer.include_router(api_router)

# Get frontend dist path
dist_path = Path(__file__).parent.parent / "frontend" / "dist"

# Mount static files
if dist_path.exists():
    app_customer.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")

# Catch-all route for React Router (excluding API paths)
@app_customer.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Skip API paths
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    # Return index.html for all other paths (React Router)
    index_file = dist_path / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(status_code=404, detail="Frontend not built. Run 'make build-ui' first.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_customer, host="0.0.0.0", port=8001)
