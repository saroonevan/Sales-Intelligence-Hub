# Sales-Intelligence-Hub

# 💎 Sales Intelligence Hub

> **Capstone Project | GUVI Master Data Science Program (IIT Madras Incubated)**

A full-stack, role-based **Branch-Based Sales Management System** built using Python, MySQL, and Streamlit — designed to solve real business problems in multi-branch organisations.


---

## 📌 Problem Statement

Organisations operating across multiple branches face challenges in:

- Tracking sales and payment collections consistently
- Manual payment calculations that drift and become inaccurate over time
- Lack of real-time visibility into pending collections per branch
- No accountability or transparency between branches
- Duplicate entries and inconsistent financial records

**This project solves all of it — automatically.**

---

## 🎯 Domain

**Sales Analytics & Financial Tracking System**

---

## 🖥️ App Overview

| Page | Role | Description |
|------|------|-------------|
| 🔐 Login | All | Secure session-based authentication |
| 📊 Dashboard | All | KPI cards, charts, data table, CSV export |
| ➕ Add Sale | Admin / Super Admin | Record new enrollments with duplicate prevention |
| 💳 Payments | Admin / Super Admin | Split payments, history, undo with recalculation |
| 🗄️ SQL Explorer | All | 20 live business queries, executable inside the app |

---

## 🔐 Role-Based Access Control

| Role | Access |
|------|--------|
| **Super Admin** | Full access across all 8 branches — filter, delete, export, all analytics |
| **Admin** | Own branch only — add sales, record payments, track pending |

> Admins are strictly isolated — they cannot view, edit, or delete data from any other branch.

---

## 🗄️ Database Design (MySQL)

### Tables

```
branches_table    — Branch information (8 cities)
customer_sales    — All sales transactions (main financial table)
users_table       — Login credentials and role assignments
payment_splits    — Multiple payment records per sale
```

### Schema

```sql
-- Branch info
CREATE TABLE branches_table (
    branch_id         INT AUTO_INCREMENT PRIMARY KEY,
    branch_name       VARCHAR(100),
    branch_admin_name VARCHAR(100)
);

-- Sales transactions
CREATE TABLE customer_sales (
    sale_id          INT AUTO_INCREMENT PRIMARY KEY,
    branch_id        INT,
    D_O_S            DATE,
    name             VARCHAR(100),
    mobile_number    VARCHAR(15),
    product_name     VARCHAR(30),
    gross_sales      DECIMAL(12,2),
    received_amount  DECIMAL(12,2),
    pending_amount   DECIMAL(12,2) GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status           ENUM('Open','Close') DEFAULT 'Open',
    FOREIGN KEY (branch_id) REFERENCES branches_table(branch_id)
);

-- User accounts
CREATE TABLE users_table (
    user_id   INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(100),
    password  VARCHAR(255),
    branch_id INT,
    role      ENUM('Super Admin','Admin'),
    email     VARCHAR(255) UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches_table(branch_id)
);

-- Split payment records
CREATE TABLE payment_splits (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    sale_id        INT,
    payment_date   DATE,
    amount_paid    DECIMAL(12,2),
    payment_method VARCHAR(50),
    FOREIGN KEY (sale_id) REFERENCES customer_sales(sale_id)
);
```

### 🔁 MySQL Trigger (Automation)

```sql
-- Fires AFTER every INSERT on payment_splits
-- Auto-updates received_amount in customer_sales
-- pending_amount adjusts automatically (GENERATED COLUMN)

DELIMITER $$
CREATE TRIGGER update_received_amount
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = received_amount + NEW.amount_paid
    WHERE sale_id = NEW.sale_id;
END$$
DELIMITER ;
```

> ⚠️ **Critical:** Because this trigger exists, the app does **NOT** manually update `received_amount` after an INSERT. Doing both causes double-counting and negative pending amounts.

### Table Relationships

```
branches_table  (1) ──→ (Many)  customer_sales
customer_sales  (1) ──→ (Many)  payment_splits
branches_table  (1) ──→ (Many)  users_table
```

---

## ⚙️ Features

### 📊 Dashboard
- 4 live KPI cards — Total Sales | Collected | Pending | Total Records
- Plotly donut chart — Collected vs Pending breakdown
- Plotly bar chart — Revenue by Product
- Plotly horizontal bar — Branch-wise revenue (Super Admin only)
- Searchable data table with branch, product, and date range filters
- One-click CSV export

### ➕ Add Sales
- Branch-locked for Admin (cannot select other branches)
- Duplicate entry prevention — same customer + product + amount = blocked
- Supports 8 course types: `DS` `BA` `DA` `FSD` `ML` `AI` `BI` `SQL`

### 💳 Payments
- Split payment support — multiple payments per sale
- Full payment history with date, amount, method
- Undo/remove payment — recalculates `received_amount` using `SUM()` for accuracy
- Auto status update — `Open` → `Close` when `pending_amount = ₹0`
- Double-submission guard via `session_state` flag

### 🗄️ SQL Explorer — 20 Live Queries

| Category | Queries |
|----------|---------|
| Basic (4) | All sales, branches, payments, open sales, Chennai sales |
| Aggregation (4) | Total gross, total received, total pending, count per branch, average |
| JOIN-Based (4) | Sales + branch name, sales + payments, branch totals, payment method |
| Financial (4) | High pending, top 3 sales, top branch, monthly summary, method totals |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Web Framework | Streamlit |
| Database | MySQL 8.0 |
| ORM/Connector | mysql-connector-python |
| Charts | Plotly Express + Plotly Graph Objects |
| Data Processing | Pandas |
| Authentication | Streamlit Session State |
| UI Styling | Custom CSS (Space Grotesk + Inter fonts, dark theme) |
| DB Automation | MySQL Triggers + Generated Columns |

---

## 📊 Data Scale

| Table | Records |
|-------|---------|
| Branches | 8 cities across India |
| Users | 9 (1 Super Admin + 8 Branch Admins) |
| Customer Sales | 1,000 records |
| Payment Splits | 2,011 transactions |
| **Total Gross Sales** | **₹3.67 Crore** |
| **Total Collected** | **₹1.90 Crore** |

---

## 🐛 Real Bugs Fixed During Development

This project went through real debugging. Here's what broke and how it was fixed:

### Bug #1 — Double Payment / Negative Pending Amount
**Symptom:** Customer with ₹50,000 gross sales showed ₹-30,000 pending after a ₹40,000 payment.
**Root Cause:** MySQL TRIGGER auto-updated `received_amount` after INSERT. App was *also* running `UPDATE received_amount = received_amount + amount`. Double-counted.
**Fix:** Removed the manual `UPDATE`. Trigger is the single source of truth.

### Bug #2 — `Unread result found` (MySQL InternalError)
**Symptom:** Dashboard crashed on load.
**Root Cause:** 4 cursors sharing 1 cached `@st.cache_resource` connection. MySQL cannot handle multiple unread result sets on one connection simultaneously.
**Fix:** Every query now opens a **fresh connection** with `buffered=True`, fetches all results, and closes immediately. No shared state.

### Bug #3 — Foreign Key Constraint on Delete
**Symptom:** `IntegrityError 1451` when deleting a sale that had payments linked to it.
**Root Cause:** Tried to delete parent row (`customer_sales`) while child rows (`payment_splits`) still referenced it.
**Fix:** Delete `payment_splits` first (children), then `customer_sales` (parent). Order matters.

### Bug #4 — Empty Box on Login Page
**Symptom:** A blank grey box appeared above the login form inputs.
**Root Cause:** Opened `<div class="card">` in one `st.markdown()` call, rendered Streamlit widgets, then closed `</div>` in another call. Streamlit strips unclosed HTML between render cycles — the div rendered as an empty box with nothing inside.
**Fix:** Removed all HTML wrappers around Streamlit widgets. HTML is purely decorative. Clean separation throughout.

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/saroonevan/Sales-Intelligence-Hub.git
cd Sales-Intelligence-Hub
```

### 2. Install dependencies
```bash
pip install streamlit mysql-connector-python pandas plotly
```

### 3. Set up MySQL
- Create the database: `SN_FashionInstitute`
- Run the schema SQL to create all 4 tables
- Create the `update_received_amount` trigger
- Insert your branch, user, and sales data

### 4. Update DB credentials
```python
# In sales_intelligence_hub.py, find DB_CONFIG and update:
DB_CONFIG = dict(
    host="localhost",
    user="your_username",
    password="your_password",
    database="SN_FashionInstitute"
)
```

### 5. Launch the app
```bash
streamlit run sales_intelligence_hub.py
```

### 6. Default login credentials
| Role | Username | Password |
|------|----------|----------|
| Super Admin | `superadmin` | `super123` |
| Chennai Admin | `admin_chennai` | `admin123` |
| Bangalore Admin | `admin_bangalore` | `admin123` |

> Update credentials in your `users_table` as needed.

---

## 📁 Project Structure

```
Sales-Intelligence-Hub/
│
├── sales_intelligence_hub.py   # Main Streamlit app (1,004 lines)
└── README.md                   # Project documentation
```

---

## 💡 Key Engineering Decisions

**Why fresh DB connections instead of a cached shared one?**
Streamlit reruns the entire script on every user interaction. A single cached connection shared across multiple cursor operations causes MySQL's `Unread result found` error. Fresh connections per query — opened, used, and closed immediately — are stable and safe.

**Why `buffered=True` on all cursors?**
Buffered cursors fetch all rows into memory immediately on execute. Without buffering, MySQL holds the result set open server-side, and any new query on the same connection throws `Unread result found`.

**Why recalculate `received_amount` from `SUM()` on payment removal instead of subtracting?**
Subtraction can drift if any edge case is missed. Recalculating from `SUM(payment_splits.amount_paid)` is always 100% accurate regardless of history — the safest approach for financial data.

**Why a GENERATED COLUMN for `pending_amount`?**
It can never get out of sync. `pending_amount = gross_sales - received_amount` is computed directly by MySQL — not by the app. Any update to either column automatically reflects in pending.

---

## 📋 Project Deliverables (GUVI Requirements)

| Deliverable | Status |
|------------|--------|
| MySQL database schema | ✅ |
| Trigger implementation | ✅ |
| Sample data (1,000 sales, 2,011 payments) | ✅ |
| 20 SQL analytical queries (live in app) | ✅ |
| Python-MySQL connection script | ✅ |
| Streamlit dashboard | ✅ |
| Documentation (this README) | ✅ |

---

## 👨‍💻 Author

**Saroon** — Team Lead, AnnexMed Pvt. Ltd. | Data Science Learner
- 7+ years experience in US Healthcare Revenue Cycle Management (RCM)
- Transitioning to: Data Scientist | ML Engineer | AI Engineer
- Certified: GUVI Master Data Science Program — IIT Madras Incubated (June 2026)

📧 saroon.akon@gmail.com
🔗 [GitHub](https://github.com/saroonevan)
📍 Chennai, Tamil Nadu | Open to USA, UAE, UK

---

## 🙏 Acknowledgement

Special thanks to my mentor **Vignesh P** — for every bug, every breakdown, and every breakthrough that made this project what it is.

---

## 🏷️ Technical Tags

`Python` `MySQL` `SQL Triggers` `Generated Columns` `Streamlit` `Plotly` `Pandas` `Financial Analytics` `Sales Management System` `Role-Based Access Control` `Data Science` `Capstone Project`

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
