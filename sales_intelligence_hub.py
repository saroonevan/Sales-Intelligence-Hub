import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS — Dark Premium Theme
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg:       #0D0F14;
    --bg-card:  #13161E;
    --bg-hover: #1A1E28;
    --accent:   #6C63FF;
    --accent-s: rgba(108,99,255,0.15);
    --green:    #00D4AA;
    --red:      #FF6B6B;
    --gold:     #FFB347;
    --text:     #F0F2F8;
    --muted:    #8892A4;
    --border:   rgba(108,99,255,0.2);
    --border-s: rgba(255,255,255,0.06);
    --r:        14px;
    --r-sm:     8px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.main .block-container { padding: 1.5rem 2rem; max-width: 1400px; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border-s);
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }

/* ── Select / Inputs ── */
div[data-baseweb="select"] > div {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
}
div[data-baseweb="select"] svg { color: var(--muted) !important; }
div[data-baseweb="popover"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; }
li[role="option"] { background: var(--bg-card) !important; color: var(--text) !important; }
li[role="option"]:hover { background: var(--bg-hover) !important; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    padding: 0.6rem 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-s) !important;
}
label[data-testid="stWidgetLabel"] > div > p {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #8B84FF) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--r-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(108,99,255,0.4) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

.stDownloadButton > button {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    background: var(--accent-s) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Alerts ── */
.stSuccess > div {
    background: rgba(0,212,170,0.08) !important;
    border: 1px solid rgba(0,212,170,0.3) !important;
    border-radius: var(--r-sm) !important;
    color: var(--green) !important;
}
.stError > div {
    background: rgba(255,107,107,0.08) !important;
    border: 1px solid rgba(255,107,107,0.3) !important;
    border-radius: var(--r-sm) !important;
    color: var(--red) !important;
}
.stWarning > div {
    background: rgba(255,179,71,0.08) !important;
    border: 1px solid rgba(255,179,71,0.3) !important;
    border-radius: var(--r-sm) !important;
    color: var(--gold) !important;
}
.stInfo > div {
    background: var(--accent-s) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
}

/* ── DataFrames ── */
.stDataFrame { border-radius: var(--r) !important; overflow: hidden !important; }
.stDataFrame thead tr th {
    background: var(--bg-hover) !important;
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: var(--bg-hover) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-s) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r-sm) var(--r-sm) !important;
}

/* ── Checkbox ── */
.stCheckbox label { color: var(--muted) !important; font-size: 0.85rem !important; }

/* ── Code blocks ── */
.stCode, code {
    background: var(--bg) !important;
    border: 1px solid var(--border-s) !important;
    border-radius: var(--r-sm) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border-s);
    border-radius: var(--r);
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.78rem !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; }

/* ── Radio nav ── */
div[data-testid="stRadio"] > div { gap: 0.25rem !important; flex-direction: column !important; }
div[data-testid="stRadio"] label {
    border-radius: var(--r-sm) !important;
    padding: 0.55rem 0.8rem !important;
    color: var(--muted) !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
    transition: all 0.15s;
    width: 100%;
}
div[data-testid="stRadio"] label:hover {
    background: var(--bg-hover) !important;
    color: var(--text) !important;
}

/* ── Reusable HTML components ── */
.page-header-block {
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border-s);
    margin-bottom: 1.8rem;
}
.page-eyebrow {
    font-size: 0.68rem; font-weight: 600;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--accent); margin: 0 0 0.3rem 0;
}
.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem; font-weight: 700;
    letter-spacing: -0.03em; color: var(--text);
    margin: 0 0 0.3rem 0; line-height: 1.2;
}
.page-desc { font-size: 0.85rem; color: var(--muted); margin: 0; }

.card-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border-s);
    border-radius: var(--r);
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.2rem;
}
.card-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.92rem; font-weight: 600;
    color: var(--text); margin: 0 0 1rem 0;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--border-s);
    display: flex; align-items: center; gap: 0.5rem;
}
.dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent); display: inline-block; flex-shrink: 0;
}

.kpi-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border-s);
    border-radius: var(--r);
    padding: 1.3rem 1.4rem;
    position: relative; overflow: hidden;
    margin-bottom: 0.5rem;
}
.kpi-wrap::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: var(--r) var(--r) 0 0;
}
.kpi-purple::before { background: var(--accent); }
.kpi-green::before  { background: var(--green); }
.kpi-red::before    { background: var(--red); }
.kpi-gold::before   { background: var(--gold); }
.kpi-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem; }
.kpi-value { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
.kpi-purple .kpi-value { color: var(--accent); }
.kpi-green  .kpi-value { color: var(--green); }
.kpi-red    .kpi-value { color: var(--red); }
.kpi-gold   .kpi-value { color: var(--gold); }
.kpi-icon { position: absolute; top: 1rem; right: 1.2rem; font-size: 1.5rem; opacity: 0.2; }

.info-pill {
    background: var(--accent-s); border: 1px solid var(--border);
    border-radius: var(--r-sm); padding: 0.7rem 1rem;
    font-size: 0.85rem; color: var(--text); margin-bottom: 1rem;
}
.hr { border: none; border-top: 1px solid var(--border-s); margin: 1.2rem 0; }

/* ── Sidebar branding ── */
.sb-brand { text-align: center; padding: 1rem 0 1.5rem; border-bottom: 1px solid var(--border-s); margin-bottom: 1.5rem; }
.sb-brand-name { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: var(--text); }
.sb-brand-sub { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin-top: 0.2rem; }
.sb-user { background: var(--accent-s); border: 1px solid var(--border); border-radius: var(--r); padding: 0.8rem 1rem; margin-bottom: 1.4rem; display: flex; align-items: center; gap: 0.75rem; }
.sb-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, var(--accent), var(--green)); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.95rem; color: #fff; flex-shrink: 0; }
.sb-name { font-weight: 600; font-size: 0.88rem; color: var(--text); }
.sb-role { font-size: 0.7rem; color: var(--accent); font-weight: 500; }
.sb-nav-label { font-size: 0.62rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); padding: 0 0.3rem; margin-bottom: 0.4rem; }

/* ── Login page ── */
.login-hero-block {
    text-align: center;
    padding: 4rem 0 2rem 0;
}
.login-hero-block .gem { font-size: 3.5rem; display: block; margin-bottom: 1rem; }
.login-hero-block h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem; font-weight: 700;
    letter-spacing: -0.04em; color: var(--text); margin: 0;
}
.login-hero-block .tagline { font-size: 0.85rem; color: var(--muted); margin-top: 0.4rem; }
.login-form-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem; font-weight: 600;
    color: var(--text); margin-bottom: 1.2rem;
    padding: 1.4rem 0 0.8rem 0;
    border-top: 1px solid var(--border-s);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DATABASE HELPERS
# Each function opens a fresh connection, runs, and closes.
# This prevents "Unread result found" on shared connections.
# ══════════════════════════════════════════════════════════════
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="Evan@1995",
    database="SN_FashionInstitute"
)

def new_conn():
    """Open a fresh MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

def run_query(sql, params=(), one=False):
    """
    Run a SELECT query.
    Returns a single dict (one=True) or list of dicts (one=False).
    Opens connection, fetches ALL results with buffered=True, then closes.
    """
    conn = new_conn()
    cur  = conn.cursor(dictionary=True, buffered=True)
    cur.execute(sql, params)
    result = cur.fetchone() if one else cur.fetchall()
    cur.close()
    conn.close()
    return result

def run_write(statements):
    """
    Run one or more write statements (INSERT / UPDATE / DELETE) atomically.
    statements: list of (sql, params) tuples.
    Commits on success, rolls back on error.
    """
    conn = new_conn()
    cur  = conn.cursor(buffered=True)
    try:
        for sql, params in statements:
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None


# ══════════════════════════════════════════════════════════════
# LOGIN PAGE
# No HTML div wraps around Streamlit widgets — avoids empty boxes
# ══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    _, col_m, _ = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
        <div class="login-hero-block">
            <span class="gem">💎</span>
            <h1>Sales Intelligence Hub</h1>
            <p class="tagline">SN Fashion Institute · Powered by Data</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="login-form-label">Sign in to your account</p>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", placeholder="••••••••", type="password")
        st.write("")

        if st.button("Sign In →", use_container_width=True):
            user = run_query(
                "SELECT * FROM users_table WHERE username=%s AND password=%s",
                (username, password), one=True
            )
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Incorrect username or password. Please try again.")
    st.stop()


# ══════════════════════════════════════════════════════════════
# MAIN APP — authenticated from here
# ══════════════════════════════════════════════════════════════
user      = st.session_state.user
role      = user["role"]
branch_id = user["branch_id"]
uname     = user["username"]
avatar    = uname[0].upper()

# Product list matching your actual database values
PRODUCTS = ["DS", "BA", "DA", "FSD", "ML", "AI", "BI", "SQL"]

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-brand-name">💎 SN Fashion</div>
        <div class="sb-brand-sub">Sales Intelligence Hub</div>
    </div>
    <div class="sb-user">
        <div class="sb-avatar">{avatar}</div>
        <div>
            <div class="sb-name">{uname}</div>
            <div class="sb-role">{role}</div>
        </div>
    </div>
    <div class="sb-nav-label">Navigation</div>
    """, unsafe_allow_html=True)

    nav_map = {
        "📊  Dashboard":    "Dashboard",
        "➕  Add Sale":     "Add Sales",
        "💳  Payments":     "Add Payments",
        "🗄️  SQL Explorer": "SQL Questions",
    }
    page = nav_map[st.radio("", list(nav_map.keys()), label_visibility="collapsed")]

    st.write("")
    st.write("")
    st.markdown('<div class="sb-nav-label">Account</div>', unsafe_allow_html=True)
    if st.button("⏏  Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()


# ══════════════════════════════════════════════════════════════
# ADD SALES
# ══════════════════════════════════════════════════════════════
if page == "Add Sales":
    st.markdown("""
    <div class="page-header-block">
        <p class="page-eyebrow">Sales Management</p>
        <h1 class="page-title">Add New Sale</h1>
        <p class="page-desc">Record a new student enrollment or product sale</p>
    </div>
    """, unsafe_allow_html=True)

    branches     = run_query("SELECT branch_id, branch_name FROM branches_table")
    branch_dict  = {b["branch_name"]: b["branch_id"] for b in branches}

    st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Sale Details</p>', unsafe_allow_html=True)

    if role == "Admin":
        bn_row = run_query(
            "SELECT branch_name FROM branches_table WHERE branch_id=%s",
            (branch_id,), one=True
        )
        bn = bn_row["branch_name"] if bn_row else f"Branch {branch_id}"
        st.markdown(f'<div class="info-pill">🏢 Branch locked to: <strong>{bn}</strong></div>', unsafe_allow_html=True)
    else:
        sel_branch = st.selectbox("Branch", list(branch_dict.keys()))
        branch_id  = branch_dict[sel_branch]

    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Full name")
    with col2:
        mobile = st.text_input("Mobile Number", placeholder="10-digit number")

    product = st.selectbox("Course / Product", PRODUCTS)
    gross   = st.number_input("Gross Sales Amount (₹)", min_value=0.0, step=500.0, format="%.2f")

    st.markdown('</div>', unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button("➕  Record Sale", use_container_width=True):
            if not customer_name.strip() or not mobile.strip():
                st.error("Please fill in Customer Name and Mobile Number.")
            elif gross <= 0:
                st.error("Gross sales amount must be greater than zero.")
            else:
                dup = run_query(
                    """SELECT 1 FROM customer_sales
                       WHERE name=%s AND mobile_number=%s AND product_name=%s
                       AND branch_id=%s AND gross_sales=%s""",
                    (customer_name, mobile, product, branch_id, gross), one=True
                )
                if dup:
                    st.warning("⚠️ Duplicate entry detected — this sale already exists.")
                else:
                    run_write([(
                        """INSERT INTO customer_sales
                           (branch_id, name, mobile_number, product_name,
                            gross_sales, received_amount, D_O_S)
                           VALUES (%s,%s,%s,%s,%s,0,CURDATE())""",
                        (branch_id, customer_name, mobile, product, gross)
                    )])
                    st.success(f"✅ Sale recorded for **{customer_name}** — ₹{gross:,.2f}")


# ══════════════════════════════════════════════════════════════
# ADD PAYMENTS  — double-submission guard prevents duplicate payments
# ══════════════════════════════════════════════════════════════
elif page == "Add Payments":
    st.markdown("""
    <div class="page-header-block">
        <p class="page-eyebrow">Payment Management</p>
        <h1 class="page-title">Record Payment</h1>
        <p class="page-desc">Add, view, or remove payments against a sale</p>
    </div>
    """, unsafe_allow_html=True)

    if role == "Admin":
        sales = run_query(
            "SELECT sale_id,name,product_name,pending_amount FROM customer_sales WHERE branch_id=%s",
            (branch_id,)
        )
    else:
        sales = run_query(
            "SELECT sale_id,name,product_name,pending_amount FROM customer_sales"
        )

    if not sales:
        st.warning("No sales records found.")
        st.stop()

    sale_dict = {
        f"#{s['sale_id']}  {s['name']}  ·  {s['product_name']}  ·  ₹{s['pending_amount']} pending": s
        for s in sales
    }

    st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Select Sale</p>', unsafe_allow_html=True)
    selected = st.selectbox("Choose a sale record", list(sale_dict.keys()))
    sale     = sale_dict[selected]
    st.markdown('</div>', unsafe_allow_html=True)

    pending = float(sale["pending_amount"])

    # ── KPI row ──
    c1, c2 = st.columns(2)
    with c1:
        colour = "green" if pending == 0 else "red"
        icon   = "✅" if pending == 0 else "⏳"
        st.markdown(f"""
        <div class="kpi-wrap kpi-{colour}">
            <div class="kpi-label">Pending Amount</div>
            <div class="kpi-value">₹{pending:,.0f}</div>
            <div class="kpi-icon">{icon}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-wrap kpi-purple">
            <div class="kpi-label">Sale ID</div>
            <div class="kpi-value">#{sale['sale_id']}</div>
            <div class="kpi-icon">🧾</div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── Add Payment ──
    st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Add Payment</p>', unsafe_allow_html=True)

    if pending <= 0:
        st.success("✅ Fully paid — no outstanding balance.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            pay_method = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Bank Transfer"])
        with col2:
            pay_amount = st.number_input(
                f"Amount (max ₹{pending:,.2f})",
                min_value=0.01, max_value=float(pending),
                step=100.0, format="%.2f"
            )

        st.write("")
        col_btn, _ = st.columns([1, 2])
        with col_btn:
            # ── Double-submission guard ──
            # Sets a flag BEFORE DB write so a second click is blocked
            guard_key = f"pay_guard_{sale['sale_id']}"
            if guard_key not in st.session_state:
                st.session_state[guard_key] = False

            if not st.session_state[guard_key]:
                if st.button("💳  Confirm Payment", use_container_width=True):
                    st.session_state[guard_key] = True   # lock immediately
                    # ── TRIGGER NOTE ──────────────────────────────────────────
                    # Your MySQL TRIGGER (update_received_amount) fires AFTER
                    # INSERT on payment_splits and auto-updates received_amount.
                    # So we ONLY insert — never manually UPDATE received_amount.
                    # Adding that UPDATE on top of the trigger = double-counting
                    # = negative pending_amount (the bug you saw).
                    # ──────────────────────────────────────────────────────────
                    run_write([
                        ("INSERT INTO payment_splits (sale_id,payment_date,amount_paid,payment_method) VALUES (%s,CURDATE(),%s,%s)",
                         (sale["sale_id"], pay_amount, pay_method)),
                        # Status flip runs after trigger has updated received_amount
                        ("UPDATE customer_sales SET status='Close' WHERE sale_id=%s AND pending_amount<=0",
                         (sale["sale_id"],)),
                    ])
                    st.session_state[guard_key] = False  # unlock after commit
                    st.success(f"✅ ₹{pay_amount:,.2f} via {pay_method} recorded!")
                    st.rerun()
            else:
                st.info("⏳ Processing payment…")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Payment History ──
    st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Payment History</p>', unsafe_allow_html=True)

    payments = run_query(
        "SELECT payment_id,payment_date,amount_paid,payment_method FROM payment_splits WHERE sale_id=%s ORDER BY payment_id DESC",
        (sale["sale_id"],)
    )

    if not payments:
        st.info("No payments recorded for this sale yet.")
    else:
        df_pay = pd.DataFrame(payments)
        df_pay.columns = ["ID", "Date", "Amount (₹)", "Method"]
        st.dataframe(df_pay, hide_index=True, use_container_width=True)
        st.caption(f"{len(payments)} payment(s) found")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown("**Remove a Payment**")

        pay_opts = {
            f"ID#{p['payment_id']}  ·  {p['payment_date']}  ·  ₹{p['amount_paid']}  [{p['payment_method']}]": p
            for p in payments
        }
        sel_pay  = st.selectbox("Select payment to remove", list(pay_opts.keys()))
        pay_rm   = pay_opts[sel_pay]
        confirm_rm = st.checkbox(f"Confirm removal of ₹{pay_rm['amount_paid']}")

        col_r, _ = st.columns([1, 2])
        with col_r:
            if st.button("🗑  Remove Payment", use_container_width=True):
                if not confirm_rm:
                    st.warning("Please tick the confirmation checkbox first.")
                else:
                    # No AFTER DELETE trigger exists, so we manually
                    # subtract the amount and recalculate status.
                    run_write([
                        ("DELETE FROM payment_splits WHERE payment_id=%s",
                         (pay_rm["payment_id"],)),
                        # Recalculate received_amount from payment_splits — safest approach
                        ("""UPDATE customer_sales
                            SET received_amount = (
                                SELECT COALESCE(SUM(amount_paid),0)
                                FROM payment_splits
                                WHERE sale_id = %s
                            ),
                            status = 'Open'
                            WHERE sale_id = %s""",
                         (sale["sale_id"], sale["sale_id"])),
                    ])
                    st.success(f"✅ Removed ₹{pay_rm['amount_paid']} payment.")
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
elif page == "Dashboard":
    st.markdown("""
    <div class="page-header-block">
        <p class="page-eyebrow">Analytics</p>
        <h1 class="page-title">Sales Dashboard</h1>
        <p class="page-desc">Real-time overview of sales performance across all branches</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ──
    st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Filters</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.5])
    with col1: search_name = st.text_input("Search Customer", placeholder="Type a name…")
    with col3: start_date  = st.date_input("From", value=date(2024, 1, 1))
    with col4: end_date    = st.date_input("To",   value=date.today())

    if role == "Super Admin":
        brs = run_query("SELECT branch_name FROM branches_table")
        prs = run_query("SELECT DISTINCT product_name FROM customer_sales")
        bl  = ["All Branches"] + [b["branch_name"] for b in brs]
        pl  = ["All Products"]  + [p["product_name"] for p in prs]
        with col2: sel_br = st.selectbox("Branch",  bl)
        sel_pr = st.selectbox("Product", pl)

        joins = "FROM customer_sales cs JOIN branches_table bt ON cs.branch_id=bt.branch_id"
        where = "WHERE 1=1"
        p_s   = []
        if sel_br != "All Branches": where += " AND bt.branch_name=%s";  p_s.append(sel_br)
        if sel_pr != "All Products": where += " AND cs.product_name=%s"; p_s.append(sel_pr)
        if search_name:              where += " AND cs.name LIKE %s";     p_s.append(f"%{search_name}%")
        where += " AND DATE(cs.D_O_S) BETWEEN %s AND %s"; p_s += [start_date, end_date]

        sm_row   = run_query(
            f"SELECT SUM(cs.gross_sales) gross,SUM(cs.received_amount) received,SUM(cs.pending_amount) pending,COUNT(cs.sale_id) cnt {joins} {where}",
            tuple(p_s), one=True
        )
        tbl_rows = run_query(
            f"SELECT cs.sale_id,bt.branch_name,cs.name,cs.mobile_number,cs.product_name,cs.gross_sales,cs.received_amount,cs.pending_amount,cs.status,cs.D_O_S {joins} {where}",
            tuple(p_s)
        )
    else:
        prs = run_query("SELECT DISTINCT product_name FROM customer_sales WHERE branch_id=%s", (branch_id,))
        pl  = ["All Products"] + [p["product_name"] for p in prs]
        with col2: sel_pr = st.selectbox("Product", pl)

        where = "WHERE branch_id=%s"; p_s = [branch_id]
        if sel_pr != "All Products": where += " AND product_name=%s"; p_s.append(sel_pr)
        if search_name:              where += " AND name LIKE %s";    p_s.append(f"%{search_name}%")
        where += " AND DATE(D_O_S) BETWEEN %s AND %s"; p_s += [start_date, end_date]

        sm_row   = run_query(
            f"SELECT SUM(gross_sales) gross,SUM(received_amount) received,SUM(pending_amount) pending,COUNT(sale_id) cnt FROM customer_sales {where}",
            tuple(p_s), one=True
        )
        tbl_rows = run_query(
            f"SELECT * FROM customer_sales {where}",
            tuple(p_s)
        )

    st.markdown('</div>', unsafe_allow_html=True)

    if start_date > end_date:
        st.error("Start date cannot be after end date.")
        st.stop()

    gross    = float(sm_row["gross"]    or 0)
    received = float(sm_row["received"] or 0)
    pending  = float(sm_row["pending"]  or 0)
    count    = int(sm_row["cnt"]        or 0)

    # ── KPI Cards ──
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.4rem;">
        <div class="kpi-wrap kpi-purple">
            <div class="kpi-label">Total Sales</div>
            <div class="kpi-value">₹{gross/1e5:.1f}L</div>
            <div class="kpi-icon">💰</div>
        </div>
        <div class="kpi-wrap kpi-green">
            <div class="kpi-label">Collected</div>
            <div class="kpi-value">₹{received/1e5:.1f}L</div>
            <div class="kpi-icon">✅</div>
        </div>
        <div class="kpi-wrap kpi-red">
            <div class="kpi-label">Pending</div>
            <div class="kpi-value">₹{pending/1e5:.1f}L</div>
            <div class="kpi-icon">⏳</div>
        </div>
        <div class="kpi-wrap kpi-gold">
            <div class="kpi-label">Total Records</div>
            <div class="kpi-value">{count:,}</div>
            <div class="kpi-icon">📋</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_all = pd.DataFrame(tbl_rows)

    # ── Charts ──
    col_ch1, col_ch2 = st.columns([1, 1.6])

    with col_ch1:
        st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Collection Status</p>', unsafe_allow_html=True)
        fig1 = go.Figure(go.Pie(
            labels=["Collected", "Pending"],
            values=[received, pending],
            hole=0.65,
            marker=dict(colors=["#00D4AA", "#FF6B6B"], line=dict(color="#13161E", width=3)),
            textinfo="percent", textfont=dict(size=12, color="white")
        ))
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F2F8", family="Inter"), showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                       xanchor="center", x=0.5, font=dict(color="#8892A4", size=12)),
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[dict(
                text=f"₹{gross/1e5:.1f}L",
                x=0.5, y=0.5, font_size=20,
                showarrow=False, font_color="#F0F2F8"
            )]
        )
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_ch2:
        if not df_all.empty and "product_name" in df_all.columns:
            st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Revenue by Product</p>', unsafe_allow_html=True)
            pg = df_all.groupby("product_name")["gross_sales"].sum().reset_index()
            pg = pg.sort_values("gross_sales", ascending=False)
            fig2 = px.bar(
                pg, x="product_name", y="gross_sales",
                color="product_name",
                color_discrete_sequence=["#6C63FF","#00D4AA","#FFB347","#FF6B6B",
                                         "#A78BFA","#34D399","#FCD34D","#F87171"]
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8892A4", family="Inter", size=11),
                showlegend=False,
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title=""),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Revenue (₹)"),
                margin=dict(t=10, b=10, l=0, r=0)
            )
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Branch chart (Super Admin only) ──
    if role == "Super Admin" and not df_all.empty and "branch_name" in df_all.columns:
        st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Branch-wise Revenue</p>', unsafe_allow_html=True)
        bg = df_all.groupby("branch_name")["gross_sales"].sum().reset_index().sort_values("gross_sales", ascending=True)
        fig3 = px.bar(bg, x="gross_sales", y="branch_name", orientation="h",
                     color="gross_sales", color_continuous_scale=["#6C63FF","#00D4AA"])
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8892A4", family="Inter", size=11),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Revenue (₹)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", title=""),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Data Table ──
    if not df_all.empty:
        st.markdown('<div class="card-wrap"><p class="card-label"><span class="dot"></span>Sales Records</p>', unsafe_allow_html=True)
        st.dataframe(df_all, hide_index=True, use_container_width=True)
        st.caption(f"{len(df_all)} record(s)")

        col_dl, col_di, col_dc = st.columns([1.5, 1, 1.2])
        with col_dl:
            st.download_button(
                "⬇️ Export CSV",
                df_all.to_csv(index=False).encode("utf-8"),
                "sales_export.csv", "text/csv",
                use_container_width=True
            )
        if "sale_id" in df_all.columns:
            with col_di:
                del_id = st.selectbox("Sale ID to delete", df_all["sale_id"].tolist())
            with col_dc:
                confirm_del = st.checkbox("Confirm delete")
                if st.button("🗑  Delete Entry", use_container_width=True):
                    if confirm_del:
                        # Delete child rows (payment_splits) FIRST — foreign key constraint
                        run_write([
                            ("DELETE FROM payment_splits WHERE sale_id=%s",  (del_id,)),
                            ("DELETE FROM customer_sales  WHERE sale_id=%s", (del_id,)),
                        ])
                        st.success(f"✅ Sale #{del_id} and its payments deleted.")
                        st.rerun()
                    else:
                        st.warning("Tick the confirm checkbox first.")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No records match your current filters.")


# ══════════════════════════════════════════════════════════════
# SQL EXPLORER — 20 live queries, toggle show/hide
# ══════════════════════════════════════════════════════════════
elif page == "SQL Questions":
    st.markdown("""
    <div class="page-header-block">
        <p class="page-eyebrow">SQL Explorer</p>
        <h1 class="page-title">Live SQL Queries</h1>
        <p class="page-desc">20 business queries — view the SQL, run it, explore results</p>
    </div>
    """, unsafe_allow_html=True)

    queries = [
        ("All customer sales",
         "SELECT * FROM customer_sales;",
         "SELECT * FROM customer_sales"),

        ("All branches",
         "SELECT * FROM branches_table;",
         "SELECT * FROM branches_table"),

        ("All payment splits",
         "SELECT * FROM payment_splits;",
         "SELECT * FROM payment_splits"),

        ("Open (unpaid) sales",
         "SELECT * FROM customer_sales WHERE status = 'Open';",
         "SELECT * FROM customer_sales WHERE status='Open'"),

        ("Chennai branch sales",
         "SELECT cs.* FROM customer_sales cs JOIN branches_table bt ON cs.branch_id = bt.branch_id WHERE bt.branch_name = 'Chennai';",
         "SELECT cs.* FROM customer_sales cs JOIN branches_table bt ON cs.branch_id=bt.branch_id WHERE bt.branch_name='Chennai'"),

        ("Total gross sales",
         "SELECT SUM(gross_sales) AS total_gross FROM customer_sales;",
         "SELECT SUM(gross_sales) AS total_gross FROM customer_sales"),

        ("Total received amount",
         "SELECT SUM(received_amount) AS total_received FROM customer_sales;",
         "SELECT SUM(received_amount) AS total_received FROM customer_sales"),

        ("Total pending amount",
         "SELECT SUM(pending_amount) AS total_pending FROM customer_sales;",
         "SELECT SUM(pending_amount) AS total_pending FROM customer_sales"),

        ("Sales count per branch",
         "SELECT bt.branch_name, COUNT(cs.sale_id) AS total_sales\nFROM customer_sales cs\nJOIN branches_table bt ON cs.branch_id = bt.branch_id\nGROUP BY bt.branch_name;",
         "SELECT bt.branch_name,COUNT(cs.sale_id) AS total_sales FROM customer_sales cs JOIN branches_table bt ON cs.branch_id=bt.branch_id GROUP BY bt.branch_name"),

        ("Average gross sales",
         "SELECT AVG(gross_sales) AS avg_sale FROM customer_sales;",
         "SELECT AVG(gross_sales) AS avg_sale FROM customer_sales"),

        ("Sales with branch name",
         "SELECT cs.*, bt.branch_name\nFROM customer_sales cs\nJOIN branches_table bt ON cs.branch_id = bt.branch_id;",
         "SELECT cs.*,bt.branch_name FROM customer_sales cs JOIN branches_table bt ON cs.branch_id=bt.branch_id"),

        ("Sales with total payments received",
         "SELECT cs.*, SUM(ps.amount_paid) AS total_paid\nFROM customer_sales cs\nLEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id\nGROUP BY cs.sale_id;",
         "SELECT cs.*,SUM(ps.amount_paid) AS total_paid FROM customer_sales cs LEFT JOIN payment_splits ps ON cs.sale_id=ps.sale_id GROUP BY cs.sale_id"),

        ("Branch-wise total gross sales",
         "SELECT bt.branch_name, SUM(cs.gross_sales) AS total\nFROM customer_sales cs\nJOIN branches_table bt ON cs.branch_id = bt.branch_id\nGROUP BY bt.branch_name;",
         "SELECT bt.branch_name,SUM(cs.gross_sales) AS total FROM customer_sales cs JOIN branches_table bt ON cs.branch_id=bt.branch_id GROUP BY bt.branch_name"),

        ("Sales with payment method used",
         "SELECT cs.*, ps.payment_method\nFROM customer_sales cs\nJOIN payment_splits ps ON cs.sale_id = ps.sale_id;",
         "SELECT cs.*,ps.payment_method FROM customer_sales cs JOIN payment_splits ps ON cs.sale_id=ps.sale_id"),

        ("Sales with branch admin name",
         "SELECT cs.*, u.username AS admin_name\nFROM customer_sales cs\nJOIN users_table u ON cs.branch_id = u.branch_id\nWHERE u.role = 'Admin';",
         "SELECT cs.*,u.username AS admin_name FROM customer_sales cs JOIN users_table u ON cs.branch_id=u.branch_id WHERE u.role='Admin'"),

        ("High pending sales (> ₹5,000)",
         "SELECT * FROM customer_sales WHERE pending_amount > 5000;",
         "SELECT * FROM customer_sales WHERE pending_amount>5000"),

        ("Top 3 highest gross sales",
         "SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;",
         "SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3"),

        ("Branch with highest total sales",
         "SELECT bt.branch_name, SUM(cs.gross_sales) AS total\nFROM customer_sales cs\nJOIN branches_table bt ON cs.branch_id = bt.branch_id\nGROUP BY bt.branch_name\nORDER BY total DESC LIMIT 1;",
         "SELECT bt.branch_name,SUM(cs.gross_sales) AS total FROM customer_sales cs JOIN branches_table bt ON cs.branch_id=bt.branch_id GROUP BY bt.branch_name ORDER BY total DESC LIMIT 1"),

        ("Monthly sales summary",
         "SELECT YEAR(D_O_S) AS year, MONTH(D_O_S) AS month, SUM(gross_sales) AS total\nFROM customer_sales\nGROUP BY year, month\nORDER BY year, month;",
         "SELECT YEAR(D_O_S) AS year,MONTH(D_O_S) AS month,SUM(gross_sales) AS total FROM customer_sales GROUP BY year,month ORDER BY year,month"),

        ("Payment method-wise total collection",
         "SELECT payment_method, SUM(amount_paid) AS total\nFROM payment_splits\nGROUP BY payment_method;",
         "SELECT payment_method,SUM(amount_paid) AS total FROM payment_splits GROUP BY payment_method"),
    ]

    for i, (title, display_sql, exec_sql) in enumerate(queries, 1):
        with st.expander(f"**{i:02d}.** {title}"):
            st.code(display_sql, language="sql")
            sk = f"sql_show_{i}"
            if sk not in st.session_state:
                st.session_state[sk] = False
            col_b, _ = st.columns([1, 3])
            with col_b:
                lbl = "🔼 Hide Results" if st.session_state[sk] else "▶️ Run Query"
                if st.button(lbl, key=f"sql_btn_{i}", use_container_width=True):
                    st.session_state[sk] = not st.session_state[sk]
            if st.session_state[sk]:
                try:
                    data = run_query(exec_sql)
                    if data:
                        st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)
                        st.caption(f"{len(data)} row(s) returned")
                    else:
                        st.info("Query returned no results.")
                except Exception as e:
                    st.error(f"Query error: {e}")