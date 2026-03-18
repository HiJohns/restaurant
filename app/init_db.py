import sqlite3

def init_db():
    conn = sqlite3.connect('smartbite.db')
    cursor = conn.cursor()
    
    # 创建用户表 (支持 6 大角色)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        role TEXT CHECK(role IN ('CUSTOMER', 'CHEF', 'WAITER', 'OWNER', 'CASHIER', 'IT_ADMIN')) NOT NULL
    )''')

    # 创建订单表 (CRUD 的核心)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        status TEXT CHECK(status IN ('PENDING', 'COOKING', 'READY', 'SERVED', 'PAID')) DEFAULT 'PENDING',
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()
    print("SQLite 数据库初始化成功：smartbite.db")

if __name__ == "__main__":
    init_db()
