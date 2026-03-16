# SmartBite Ordering System - Product Definition Document (PDD)

## 1. Project Overview
A dual-interface ordering system designed for a fresh grocery/restaurant hybrid, balancing customer ease-of-use with robust internal operational controls.

---

## 2. Stakeholder Roles & Functional Requirements

### 1. 顾客 (Customer) - The Consumer
* **Core Responsibility:** Browsing dishes and placing orders.
* **Key Features:**
    * **Digital Menu:** Real-time view of dishes, prices, and availability.
    * **Self-Service Ordering:** Add items to cart with special instructions (e.g., "extra spicy").
    * **Order Tracking:** Monitor status from "Queued" to "Ready for Pickup/Service."

### 2. 厨师 (Chef) - The Producer
* **Core Responsibility:** Preparing food and managing kitchen flow.
* **Key Features:**
    * **KDS (Kitchen Display System):** View incoming orders in real-time.
    * **Status Updates:** Mark items as "Cooking" or "Completed."
    * **Inventory Control:** Mark items as "Sold Out" instantly to prevent over-ordering.

### 3. 服务员 (Waiter) - The Facilitator
* **Core Responsibility:** Table management and service delivery.
* **Key Features:**
    * **Table Map:** Real-time status of all tables (Occupied, Empty, Needs Cleaning).
    * **Delivery Tracking:** Receive alerts when a dish is ready to be served.
    * **Manual Override:** Assist customers with manual order entry.

### 4. 店主 (Owner) - The Administrator
* **Core Responsibility:** Business logic, menu curation, and financial oversight.
* **Key Features:**
    * **Menu Management:** Update dish names, descriptions, images, and pricing.
    * **Payment Gateway Config:** Manage Stripe/PayPal/Local payment integrations.
    * **Analytics:** View daily revenue, top-selling items, and peak hours.

### 5. IT 管理员 (IT Admin) - The Maintainer
* **Core Responsibility:** System stability, security, and tech stack health.
* **Key Features:**
    * **System Health Monitor:** Check Go backend, PostgreSQL DB, and Docker container status.
    * **User/Permission Management:** Assign roles (Chef, Waiter, etc.) to staff accounts.
    * **Hardware Integration:** Manage printer IP mappings and POS terminal connectivity.

### 6. 收银员 (Cashier) - The Finalizer
* **Core Responsibility:** Final payment processing and reconciliation.
* **Key Features:**
    * **Transaction Terminal:** Handle cash, card, or QR code payments.
    * **Receipt Generation:** Trigger hardware for physical or digital receipts.
    * **Refunds/Adjustments:** Process returns or price corrections at checkout.

---

## 3. Technical Implementation (Draft)
* **Backend:** Go (Gin/Echo)
* **Database:** PostgreSQL
* **Architecture:** RBAC (Role-Based Access Control)
* **Deployment:** Docker + Compose
