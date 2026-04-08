import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import date

# 🔗 DB CONNECTION
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Evan@1995",
    database="SN_FashionInstitute"
)

# 🔐 SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 🔐 LOGIN PAGE
if not st.session_state.logged_in:
    st.title("Sales Intelligence Hub")
    st.header("SN Fashion Institute")
    st.subheader("we bring Fashion from future")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users_table WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome {user['username']} ({user['role']})")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ✅ MAIN APP
else:
    user = st.session_state.user

    # 🔹 SIDEBAR
    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox("Go to", ["Dashboard", "Add Sales", "Add Payments", "SQL Questions"])

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    st.title(user["role"])
    st.header(user["username"])

    # ==================================
    # ➕ ADD SALES
    # ==================================
    if page == "Add Sales":

        st.title("➕ Add Sales")
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT branch_id, branch_name FROM branches_table")
        branches = cursor.fetchall()
        branch_dict = {b["branch_name"]: b["branch_id"] for b in branches}

        if user["role"] == "Admin":
            branch_id = user["branch_id"]
            cursor.execute("SELECT branch_name FROM branches_table WHERE branch_id=%s", (branch_id,))
            branch_name = cursor.fetchone()["branch_name"]
            st.info(f"Branch: {branch_name}")
        else:
            selected_branch = st.selectbox("Select Branch", list(branch_dict.keys()))
            branch_id = branch_dict[selected_branch]

        customer_name = st.text_input("Customer Name", key="cust_name")
        mobile = st.text_input("Mobile Number", key="mobile")

        product = st.selectbox(
            "Product Type",
            ["Fashion Design", "Fashion Illustration", "Knitwear Design", "Textile Design"]
        )

        gross = st.number_input("Gross Sales", min_value=0.0)

        if st.button("Add Sale"):
            if not customer_name or not mobile:
                st.error("Please fill all fields")
            else:
                cursor.execute("""
                    SELECT 1 FROM customer_sales 
                    WHERE name=%s AND mobile_number=%s AND product_name=%s 
                    AND branch_id=%s AND gross_sales=%s
                """, (customer_name, mobile, product, branch_id, gross))

                if cursor.fetchone():
                    st.warning("⚠️ Duplicate entry not allowed")
                else:
                    cursor.execute("""
                        INSERT INTO customer_sales 
                        (branch_id, name, mobile_number, product_name, gross_sales, received_amount, D_O_S)
                        VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
                    """, (branch_id, customer_name, mobile, product, gross, 0))

                    conn.commit()
                    st.success("✅ Sale Added Successfully")

    # ==================================
    # 💰 ADD PAYMENTS
    # ==================================
    elif page == "Add Payments":

        st.title("💰 Add Payment")
        cursor = conn.cursor(dictionary=True)

        role = user["role"]
        branch_id = user["branch_id"]

        if role == "Admin":
            cursor.execute("""
                SELECT sale_id, name, product_name, pending_amount
                FROM customer_sales
                WHERE branch_id=%s
            """, (branch_id,))
        else:
            cursor.execute("""
                SELECT sale_id, name, product_name, pending_amount
                FROM customer_sales
            """)

        sales = cursor.fetchall()

        if not sales:
            st.warning("No sales found!")
        else:
            sale_dict = {
                f"{s['sale_id']} | {s['name']} | {s['product_name']} | Pending ₹{s['pending_amount']}": s
                for s in sales
            }

            selected = st.selectbox("Select Sale", list(sale_dict.keys()))
            sale = sale_dict[selected]

            st.markdown("---")

            # ➕ ADD NEW PAYMENT
            st.subheader("➕ Add New Payment")

            if float(sale["pending_amount"]) <= 0:
                st.success("✅ This sale is fully paid!")
            else:
                payment_method = st.selectbox(
                    "Payment Method",
                    ["Cash", "UPI", "Card", "Bank Transfer"]
                )
                payment = st.number_input("Enter Payment Amount", min_value=0.0)

                if st.button("Add Payment"):
                    if payment <= 0:
                        st.error("Enter valid amount")
                    elif payment > float(sale["pending_amount"]):
                        st.error("Payment exceeds pending amount")
                    else:
                        cursor.execute("""
                            INSERT INTO payment_splits (sale_id, payment_date, amount_paid, payment_method)
                            VALUES (%s, CURDATE(), %s, %s)
                        """, (sale["sale_id"], payment, payment_method))

                        cursor.execute("""
                            UPDATE customer_sales
                            SET received_amount = received_amount + %s
                            WHERE sale_id = %s
                        """, (payment, sale["sale_id"]))

                        cursor.execute("""
                            UPDATE customer_sales
                            SET status = 'Close'
                            WHERE sale_id = %s AND pending_amount = 0
                        """, (sale["sale_id"],))

                        conn.commit()
                        st.success("✅ Payment Added Successfully")
                        st.rerun()

            st.markdown("---")

            # 🗑 REMOVE A PAYMENT
            st.subheader("🗑 Remove a Payment")

            cursor2 = conn.cursor(dictionary=True)
            cursor2.execute("""
                SELECT payment_id, payment_date, amount_paid, payment_method
                FROM payment_splits
                WHERE sale_id = %s
                ORDER BY payment_id DESC
            """, (sale["sale_id"],))

            payments = cursor2.fetchall()

            if not payments:
                st.warning("No payments found for this customer!")
            else:
                st.markdown("**Payment History:**")
                payments_df = pd.DataFrame(payments)
                payments_df.columns = ["Payment ID", "Date", "Amount (₹)", "Method"]
                st.dataframe(payments_df, hide_index=True, use_container_width=True)

                st.markdown("**Select Payment to Remove:**")

                payment_dict = {
                    f"ID:{p['payment_id']} | {p['payment_date']} | ₹{p['amount_paid']} | {p['payment_method']}": p
                    for p in payments
                }

                selected_payment = st.selectbox("Select Payment", list(payment_dict.keys()))
                payment_to_remove = payment_dict[selected_payment]

                st.info(f"Amount to be removed: ₹{payment_to_remove['amount_paid']}")

                confirm = st.checkbox("Confirm Remove")

                if st.button("Remove Payment"):
                    if not confirm:
                        st.warning("Please confirm before removing!")
                    else:
                        cursor2.execute("""
                            DELETE FROM payment_splits
                            WHERE payment_id = %s
                        """, (payment_to_remove["payment_id"],))

                        cursor2.execute("""
                            UPDATE customer_sales
                            SET received_amount = received_amount - %s,
                                status = 'Open'
                            WHERE sale_id = %s
                        """, (payment_to_remove["amount_paid"], sale["sale_id"]))

                        conn.commit()
                        st.success(f"✅ Payment of ₹{payment_to_remove['amount_paid']} removed successfully!")
                        st.rerun()

    # ==================================
    # 📘 SQL QUESTIONS — ALL INSIDE ONE BLOCK
    # ==================================
    elif page == "SQL Questions":

        st.title("📘 SQL Questions")
        cursor = conn.cursor(dictionary=True)

        # --- Question 1 ---
        with st.expander("📌 1. Retrieve all records from the customer_sales table"):
            st.code("SELECT * FROM customer_sales;", language="sql")
            if "show_q1" not in st.session_state:
                st.session_state.show_q1 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q1 else "🔼 Hide Data", key="q1"):
                st.session_state.show_q1 = not st.session_state.show_q1
            if st.session_state.show_q1:
                cursor.execute("SELECT * FROM customer_sales")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 2 ---
        with st.expander("📌 2. Retrieve all records from the branches table"):
            st.code("SELECT * FROM branches_table;", language="sql")
            if "show_q2" not in st.session_state:
                st.session_state.show_q2 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q2 else "🔼 Hide Data", key="q2"):
                st.session_state.show_q2 = not st.session_state.show_q2
            if st.session_state.show_q2:
                cursor.execute("SELECT * FROM branches_table")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 3 ---
        with st.expander("📌 3. Retrieve all records from the payment_splits table"):
            st.code("SELECT * FROM payment_splits;", language="sql")
            if "show_q3" not in st.session_state:
                st.session_state.show_q3 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q3 else "🔼 Hide Data", key="q3"):
                st.session_state.show_q3 = not st.session_state.show_q3
            if st.session_state.show_q3:
                cursor.execute("SELECT * FROM payment_splits")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 4 ---
        with st.expander("📌 4. Display all sales with status = 'Open'"):
            st.code("SELECT * FROM customer_sales WHERE status = 'Open';", language="sql")
            if "show_q4" not in st.session_state:
                st.session_state.show_q4 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q4 else "🔼 Hide Data", key="q4"):
                st.session_state.show_q4 = not st.session_state.show_q4
            if st.session_state.show_q4:
                cursor.execute("SELECT * FROM customer_sales WHERE status = 'Open'")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 5 ---
        with st.expander("📌 5. Retrieve all sales belonging to the Chennai branch"):
            st.code("""
SELECT cs.* FROM customer_sales cs
JOIN branches_table bt ON cs.branch_id = bt.branch_id
WHERE bt.branch_name = 'Chennai';
            """, language="sql")
            if "show_q5" not in st.session_state:
                st.session_state.show_q5 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q5 else "🔼 Hide Data", key="q5"):
                st.session_state.show_q5 = not st.session_state.show_q5
            if st.session_state.show_q5:
                cursor.execute("""
                    SELECT cs.* FROM customer_sales cs
                    JOIN branches_table bt ON cs.branch_id = bt.branch_id
                    WHERE bt.branch_name = 'Chennai'
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 6 ---
        with st.expander("📌 6. Calculate the total gross sales across all branches"):
            st.code("SELECT SUM(gross_sales) AS total_sales FROM customer_sales;", language="sql")
            if "show_q6" not in st.session_state:
                st.session_state.show_q6 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q6 else "🔼 Hide Data", key="q6"):
                st.session_state.show_q6 = not st.session_state.show_q6
            if st.session_state.show_q6:
                cursor.execute("SELECT SUM(gross_sales) AS total_sales FROM customer_sales")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 7 ---
        with st.expander("📌 7. Calculate the total received amount across all sales"):
            st.code("SELECT SUM(received_amount) AS total_received FROM customer_sales;", language="sql")
            if "show_q7" not in st.session_state:
                st.session_state.show_q7 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q7 else "🔼 Hide Data", key="q7"):
                st.session_state.show_q7 = not st.session_state.show_q7
            if st.session_state.show_q7:
                cursor.execute("SELECT SUM(received_amount) AS total_received FROM customer_sales")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 8 ---
        with st.expander("📌 8. Calculate the total pending amount across all sales"):
            st.code("SELECT SUM(pending_amount) AS total_pending FROM customer_sales;", language="sql")
            if "show_q8" not in st.session_state:
                st.session_state.show_q8 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q8 else "🔼 Hide Data", key="q8"):
                st.session_state.show_q8 = not st.session_state.show_q8
            if st.session_state.show_q8:
                cursor.execute("SELECT SUM(pending_amount) AS total_pending FROM customer_sales")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 9 ---
        with st.expander("📌 9. Count the total number of sales per branch"):
            st.code("""
SELECT bt.branch_name, COUNT(cs.sale_id) AS total_sales
FROM customer_sales cs
JOIN branches_table bt ON cs.branch_id = bt.branch_id
GROUP BY bt.branch_name;
            """, language="sql")
            if "show_q9" not in st.session_state:
                st.session_state.show_q9 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q9 else "🔼 Hide Data", key="q9"):
                st.session_state.show_q9 = not st.session_state.show_q9
            if st.session_state.show_q9:
                cursor.execute("""
                    SELECT bt.branch_name, COUNT(cs.sale_id) AS total_sales
                    FROM customer_sales cs
                    JOIN branches_table bt ON cs.branch_id = bt.branch_id
                    GROUP BY bt.branch_name
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 10 ---
        with st.expander("📌 10. Find the average gross sales amount"):
            st.code("SELECT AVG(gross_sales) AS avg_sales FROM customer_sales;", language="sql")
            if "show_q10" not in st.session_state:
                st.session_state.show_q10 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q10 else "🔼 Hide Data", key="q10"):
                st.session_state.show_q10 = not st.session_state.show_q10
            if st.session_state.show_q10:
                cursor.execute("SELECT AVG(gross_sales) AS avg_sales FROM customer_sales")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 11 ---
        with st.expander("📌 11. Retrieve sales details along with the branch name"):
            st.code("""
SELECT cs.*, bt.branch_name
FROM customer_sales cs
JOIN branches_table bt ON cs.branch_id = bt.branch_id;
            """, language="sql")
            if "show_q11" not in st.session_state:
                st.session_state.show_q11 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q11 else "🔼 Hide Data", key="q11"):
                st.session_state.show_q11 = not st.session_state.show_q11
            if st.session_state.show_q11:
                cursor.execute("""
                    SELECT cs.*, bt.branch_name
                    FROM customer_sales cs
                    JOIN branches_table bt ON cs.branch_id = bt.branch_id
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 12 ---
        with st.expander("📌 12. Retrieve sales details along with total payment received"):
            st.code("""
SELECT cs.*, SUM(ps.amount_paid) AS total_paid
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id;
            """, language="sql")
            if "show_q12" not in st.session_state:
                st.session_state.show_q12 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q12 else "🔼 Hide Data", key="q12"):
                st.session_state.show_q12 = not st.session_state.show_q12
            if st.session_state.show_q12:
                cursor.execute("""
                    SELECT cs.*, SUM(ps.amount_paid) AS total_paid
                    FROM customer_sales cs
                    LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
                    GROUP BY cs.sale_id
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 13 ---
        with st.expander("📌 13. Show branch-wise total gross sales"):
            st.code("""
SELECT bt.branch_name, SUM(cs.gross_sales) AS total_sales
FROM customer_sales cs
JOIN branches_table bt ON cs.branch_id = bt.branch_id
GROUP BY bt.branch_name;
            """, language="sql")
            if "show_q13" not in st.session_state:
                st.session_state.show_q13 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q13 else "🔼 Hide Data", key="q13"):
                st.session_state.show_q13 = not st.session_state.show_q13
            if st.session_state.show_q13:
                cursor.execute("""
                    SELECT bt.branch_name, SUM(cs.gross_sales) AS total_sales
                    FROM customer_sales cs
                    JOIN branches_table bt ON cs.branch_id = bt.branch_id
                    GROUP BY bt.branch_name
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 14 ---
        with st.expander("📌 14. Display sales along with payment method used"):
            st.code("""
SELECT cs.*, ps.payment_method
FROM customer_sales cs
JOIN payment_splits ps ON cs.sale_id = ps.sale_id;
            """, language="sql")
            if "show_q14" not in st.session_state:
                st.session_state.show_q14 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q14 else "🔼 Hide Data", key="q14"):
                st.session_state.show_q14 = not st.session_state.show_q14
            if st.session_state.show_q14:
                cursor.execute("""
                    SELECT cs.*, ps.payment_method
                    FROM customer_sales cs
                    JOIN payment_splits ps ON cs.sale_id = ps.sale_id
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 15 ---
        with st.expander("📌 15. Retrieve sales along with branch admin name"):
            st.code("""
SELECT cs.*, u.username AS admin_name
FROM customer_sales cs
JOIN users_table u ON cs.branch_id = u.branch_id
WHERE u.role = 'Admin';
            """, language="sql")
            if "show_q15" not in st.session_state:
                st.session_state.show_q15 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q15 else "🔼 Hide Data", key="q15"):
                st.session_state.show_q15 = not st.session_state.show_q15
            if st.session_state.show_q15:
                cursor.execute("""
                    SELECT cs.*, u.username AS admin_name
                    FROM customer_sales cs
                    JOIN users_table u ON cs.branch_id = u.branch_id
                    WHERE u.role = 'Admin'
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 16 ---
        with st.expander("📌 16. Find sales where pending amount > 5000"):
            st.code("SELECT * FROM customer_sales WHERE pending_amount > 5000;", language="sql")
            if "show_q16" not in st.session_state:
                st.session_state.show_q16 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q16 else "🔼 Hide Data", key="q16"):
                st.session_state.show_q16 = not st.session_state.show_q16
            if st.session_state.show_q16:
                cursor.execute("SELECT * FROM customer_sales WHERE pending_amount > 5000")
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 17 ---
        with st.expander("📌 17. Retrieve top 3 highest gross sales"):
            st.code("""
SELECT * FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;
            """, language="sql")
            if "show_q17" not in st.session_state:
                st.session_state.show_q17 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q17 else "🔼 Hide Data", key="q17"):
                st.session_state.show_q17 = not st.session_state.show_q17
            if st.session_state.show_q17:
                cursor.execute("""
                    SELECT * FROM customer_sales
                    ORDER BY gross_sales DESC
                    LIMIT 3
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 18 ---
        with st.expander("📌 18. Find branch with highest total gross sales"):
            st.code("""
SELECT bt.branch_name, SUM(cs.gross_sales) AS total
FROM customer_sales cs
JOIN branches_table bt ON cs.branch_id = bt.branch_id
GROUP BY bt.branch_name
ORDER BY total DESC
LIMIT 1;
            """, language="sql")
            if "show_q18" not in st.session_state:
                st.session_state.show_q18 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q18 else "🔼 Hide Data", key="q18"):
                st.session_state.show_q18 = not st.session_state.show_q18
            if st.session_state.show_q18:
                cursor.execute("""
                    SELECT bt.branch_name, SUM(cs.gross_sales) AS total
                    FROM customer_sales cs
                    JOIN branches_table bt ON cs.branch_id = bt.branch_id
                    GROUP BY bt.branch_name
                    ORDER BY total DESC
                    LIMIT 1
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 19 ---
        with st.expander("📌 19. Monthly sales summary"):
            st.code("""
SELECT YEAR(D_O_S) AS year, MONTH(D_O_S) AS month, SUM(gross_sales) AS total
FROM customer_sales
GROUP BY year, month;
            """, language="sql")
            if "show_q19" not in st.session_state:
                st.session_state.show_q19 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q19 else "🔼 Hide Data", key="q19"):
                st.session_state.show_q19 = not st.session_state.show_q19
            if st.session_state.show_q19:
                cursor.execute("""
                    SELECT YEAR(D_O_S) AS year, MONTH(D_O_S) AS month, SUM(gross_sales) AS total
                    FROM customer_sales
                    GROUP BY year, month
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

        # --- Question 20 ---
        with st.expander("📌 20. Payment method-wise total collection"):
            st.code("""
SELECT payment_method, SUM(amount_paid) AS total
FROM payment_splits
GROUP BY payment_method;
            """, language="sql")
            if "show_q20" not in st.session_state:
                st.session_state.show_q20 = False
            if st.button("▶️ Show Data" if not st.session_state.show_q20 else "🔼 Hide Data", key="q20"):
                st.session_state.show_q20 = not st.session_state.show_q20
            if st.session_state.show_q20:
                cursor.execute("""
                    SELECT payment_method, SUM(amount_paid) AS total
                    FROM payment_splits
                    GROUP BY payment_method
                """)
                data = cursor.fetchall()
                if data:
                    st.success("✅ Data Retrieved Successfully")
                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                else:
                    st.warning("No data found!")

    # ==================================
    # 📊 DASHBOARD
    # ==================================
    elif page == "Dashboard":

        st.subheader("Customer Sales Data 📊")

        search_name = st.text_input("🔍 Search by Customer Name")

        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start Date", value=date(2024, 1, 1))
        end_date = col2.date_input("End Date", value=date.today())

        if start_date > end_date:
            st.error("Start date cannot be after End date")
            st.stop()

        role = user["role"]
        branch_id = user["branch_id"]

        cursor  = conn.cursor(dictionary=True)
        cursor2 = conn.cursor(dictionary=True)
        cursor3 = conn.cursor(dictionary=True)

        # SUPER ADMIN
        if role == "Super Admin":

            cursor2.execute("SELECT branch_name FROM branches_table")
            branches = cursor2.fetchall()

            cursor3.execute("SELECT DISTINCT product_name FROM customer_sales")
            products = cursor3.fetchall()

            branch_list = ["All Branches"] + [b["branch_name"] for b in branches]
            product_list = ["All Products"] + [p["product_name"] for p in products]

            col1, col2 = st.columns(2)
            selected_branch = col1.selectbox("Select Branch", branch_list)
            selected_product = col2.selectbox("Select Product", product_list)

            query = """
            SELECT SUM(cs.gross_sales) AS gross,
                   SUM(cs.received_amount) AS received,
                   SUM(cs.pending_amount) AS pending
            FROM customer_sales cs
            JOIN branches_table bt ON cs.branch_id = bt.branch_id
            WHERE 1=1
            """
            params = []

            if selected_branch != "All Branches":
                query += " AND bt.branch_name = %s"
                params.append(selected_branch)

            if selected_product != "All Products":
                query += " AND cs.product_name = %s"
                params.append(selected_product)

            if search_name:
                query += " AND cs.name LIKE %s"
                params.append(f"%{search_name}%")

            query += " AND DATE(cs.D_O_S) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

            cursor2.execute(query, tuple(params))
            summary = cursor2.fetchone()

            query_table = """
            SELECT cs.sale_id, bt.branch_name, cs.name, cs.mobile_number,
                   cs.product_name, cs.gross_sales, cs.received_amount,
                   cs.pending_amount, cs.status, cs.D_O_S
            FROM customer_sales cs
            JOIN branches_table bt ON cs.branch_id = bt.branch_id
            WHERE 1=1
            """
            params_table = []

            if selected_branch != "All Branches":
                query_table += " AND bt.branch_name = %s"
                params_table.append(selected_branch)

            if selected_product != "All Products":
                query_table += " AND cs.product_name = %s"
                params_table.append(selected_product)

            if search_name:
                query_table += " AND cs.name LIKE %s"
                params_table.append(f"%{search_name}%")

            query_table += " AND DATE(cs.D_O_S) BETWEEN %s AND %s"
            params_table.extend([start_date, end_date])

            cursor.execute(query_table, tuple(params_table))

        # ADMIN
        else:

            cursor3.execute(
                "SELECT DISTINCT product_name FROM customer_sales WHERE branch_id=%s",
                (branch_id,)
            )
            products = cursor3.fetchall()

            product_list = ["All Products"] + [p["product_name"] for p in products]
            selected_product = st.selectbox("Select Product", product_list)

            query = """
            SELECT SUM(gross_sales) AS gross,
                   SUM(received_amount) AS received,
                   SUM(pending_amount) AS pending
            FROM customer_sales
            WHERE branch_id = %s
            """
            params = [branch_id]

            if selected_product != "All Products":
                query += " AND product_name = %s"
                params.append(selected_product)

            if search_name:
                query += " AND name LIKE %s"
                params.append(f"%{search_name}%")

            query += " AND DATE(D_O_S) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

            cursor2.execute(query, tuple(params))
            summary = cursor2.fetchone()

            query_table = """
            SELECT *
            FROM customer_sales
            WHERE branch_id = %s
            """
            params_table = [branch_id]

            if selected_product != "All Products":
                query_table += " AND product_name = %s"
                params_table.append(selected_product)

            if search_name:
                query_table += " AND name LIKE %s"
                params_table.append(f"%{search_name}%")

            query_table += " AND DATE(D_O_S) BETWEEN %s AND %s"
            params_table.extend([start_date, end_date])

            cursor.execute(query_table, tuple(params_table))

        # --- KPI METRICS ---
        gross    = summary["gross"]    or 0
        received = summary["received"] or 0
        pending  = summary["pending"]  or 0

        st.markdown("### 📊 Key Metrics")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Sales",  f"₹ {int(gross):,}")
        c2.metric("✅ Received",     f"₹ {int(received):,}")
        c3.metric("⏳ Pending",      f"₹ {int(pending):,}")

        # --- DONUT CHART ---
        fig = px.pie(
            names=["Received", "Pending"],
            values=[received, pending],
            hole=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- DATA TABLE ---
        df = pd.DataFrame(cursor.fetchall())

        if df.empty:
            st.warning("No data available")
        else:
            st.dataframe(df, hide_index=True, use_container_width=True)

            # --- EXPORT TO CSV ---
            st.markdown("### 📥 Export Data")
            excel_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download as CSV",
                data=excel_data,
                file_name="customer_sales.csv",
                mime="text/csv"
            )

            # --- DELETE ENTRY ---
            st.markdown("### 🗑 Delete Entry")
            selected_id = st.selectbox("Select Sale ID to Delete", df["sale_id"])
            confirm = st.checkbox("Confirm Delete")

            if st.button("Delete Entry"):
                if confirm:
                    cursor.execute(
                        "DELETE FROM customer_sales WHERE sale_id=%s",
                        (selected_id,)
                    )
                    conn.commit()
                    st.success("✅ Deleted successfully")
                    st.rerun()
                else:
                    st.warning("Please confirm deletion first!")