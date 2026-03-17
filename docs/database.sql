-- Ordering System Initial Schema
-- Database: PostgreSQL (Recommended)

-- 1. Roles & Users
CREATE TYPE user_role AS ENUM ('CUSTOMER', 'CHEF', 'WAITER', 'OWNER', 'CASHIER', 'IT_ADMIN');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Menu Management (Owner's Domain)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    image_url TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Orders & Workflow (Chef/Waiter/Cashier Domain)
CREATE TYPE order_status AS ENUM ('PENDING', 'COOKING', 'READY', 'SERVED', 'PAID', 'CANCELLED');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES users(id),
    table_number INT,
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    status order_status DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    menu_item_id INT REFERENCES menu_items(id),
    quantity INT NOT NULL,
    special_notes TEXT,
    subtotal DECIMAL(10, 2) NOT NULL
);

-- 4. Payments (Cashier's Domain)
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    payment_method VARCHAR(20), -- e.g., 'CASH', 'STRIPE', 'QR'
    transaction_id TEXT,
    amount_paid DECIMAL(10, 2) NOT NULL,
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
