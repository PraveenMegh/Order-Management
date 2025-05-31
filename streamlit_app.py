import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# --- Safe DB close helper ---
def safe_close(conn):
    try:
        conn.close()
    except Exception as e:
        st.warning(f"Warning closing DB: {e}")

def show_header():
    col1, col2 = st.columns([1, 9])
    with col1:
        st.image("assets/logo.jpg", width=140)
    with col2:
        st.markdown("""
            <div style='display: flex; align-items: center; height: 120px;'>
                <h1 style='margin: 0; padding-left: 0px;'>Shree Sai Industries</h1>
            </div>
        """, unsafe_allow_html=True)

def return_menu_logout(key_prefix):
    st.markdown("---")
    if st.button("⬅ Return to Main Menu", key=f"return_main_{key_prefix}"):
        st.session_state['page'] = 'Main Menu'
    if st.button("🔒 Logout", key=f"logout_{key_prefix}"):
        st.session_state['logged_in'] = False

def login_page():
    show_header()

    # ✅ Friendly Welcome Message
    st.markdown("### 👋 Welcome to Shree Sai Salt - Order Management System")
    st.markdown("Please log in with your credentials to access your department panel.")

    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_button"):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT username, password_hash, role, full_name FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password.encode(), result[1]):
            st.session_state['logged_in'] = True
            st.session_state['username'] = result[0]
            st.session_state['role'] = result[2]
            st.session_state['full_name'] = result[3]
            st.session_state['page'] = 'Main Menu'
            st.rerun()
        else:
            st.error("Invalid credentials")

# --- Main Menu ---
def main_menu():
    show_header()
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info(f"You are logged in as: `{st.session_state['role']}`")

    if st.session_state['role'] == 'Admin':
        if st.button("🔧 Admin Panel", key="admin_panel_btn"):
            st.session_state['page'] = 'Admin Panel'
            st.rerun()
        if st.button("📦 All Orders", key="all_orders_btn"):
            st.session_state['page'] = 'Orders'
            st.rerun()
        if st.button("📦 All Dispatch", key="all_dispatch_btn"):
            st.session_state['page'] = 'Dispatch'
            st.rerun()
        if st.button("📊 Reports", key="reports_btn"):
            st.session_state['page'] = 'Reports'
            st.rerun()

    elif st.session_state['role'] == 'Sales':
        if st.button("📦 Orders Page", key="orders_page_btn"):
            st.session_state['page'] = 'Orders'
            st.rerun()

    elif st.session_state['role'] == 'Dispatch':
        if st.button("📦 Dispatch Page", key="dispatch_page_btn"):
            st.session_state['page'] = 'Dispatch'
            st.rerun()

    st.markdown("---")
    if st.button("🔒 Logout", key="logout_main"):
        st.session_state['logged_in'] = False
        st.rerun()

def reports_page():
    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    from datetime import datetime
    show_header()

    st.markdown(f"### 👋 Welcome back, **{st.session_state.get('username', 'User')}**!")
    st.title("📊 Reports and Analytics")
    st.info("Track demand, dispatched summary, and performance insights.")

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    try:
        # --- Max Demand Product ---
        st.subheader("🔥 Highest Demand Product")
        c.execute('''
            SELECT product_name, SUM(quantity) as total_kg
            FROM order_products
            WHERE status = 'Original'
            GROUP BY product_name
            ORDER BY total_kg DESC
            LIMIT 1
        ''')
        result = c.fetchone()
        if result:
            st.success(f"Max Demand: {result[0]} | Total KG: {result[1]}")
        else:
            st.warning("No order data available.")

        # --- Min Demand Product ---
        st.subheader("💤 Lowest Demand Product")
        c.execute('''
            SELECT product_name, SUM(quantity) as total_kg
            FROM order_products
            WHERE status = 'Original'
            GROUP BY product_name
            HAVING total_kg > 0
            ORDER BY total_kg ASC
            LIMIT 1
        ''')
        result = c.fetchone()
        if result:
            st.info(f"Min Demand: {result[0]} | Total KG: {result[1]}")
        else:
            st.warning("No order data available.")

        # --- Demand Chart ---
        st.subheader("📈 Product Demand Chart")
        view_option = st.selectbox("View By", ["Total KG", "Amount (INR)"])

        if view_option == "Total KG":
            c.execute('''
                SELECT product_name, SUM(quantity)
                FROM order_products
                WHERE status IN ('Original', 'Dispatched')
                GROUP BY product_name
            ''')
        else:  # Amount (INR)
            c.execute('''
                SELECT product_name, SUM(quantity * price_inr)
                FROM order_products
                WHERE status IN ('Original', 'Dispatched')
                GROUP BY product_name
            ''')

        data = c.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["Product", "Value"])
            fig, ax = plt.subplots(figsize=(5, 2.5))  # Adjusted figure size
            df.set_index("Product")["Value"].plot(kind="bar", ax=ax)
            ax.set_ylabel(view_option)
            ax.set_title(f"Product-wise {view_option}")
            st.pyplot(fig)
        else:
            st.warning("No data to display.")

        # --- Dispatched Summary ---
        st.subheader("🚚 Dispatch Summary")
        c.execute('''
            SELECT 
                dp.product_name,
                SUM(dp.quantity) AS dispatched_kg,
                SUM(dp.quantity * IFNULL((
                    SELECT op.price_inr
                    FROM order_products op
                    WHERE op.order_id = dp.order_id 
                      AND op.product_name = dp.product_name 
                      AND op.status = 'Original'
                    ORDER BY op.order_product_id DESC LIMIT 1
                ), 0)) AS total_amount
            FROM order_products dp
            WHERE dp.status = 'Dispatched'
            GROUP BY dp.product_name
        ''')
        dispatched = c.fetchall()

        if dispatched:
            df = pd.DataFrame(dispatched, columns=["Product", "Dispatched KG", "Total Amount"])
            df["Total Amount"] = df["Total Amount"].fillna(0).astype(float)
            st.dataframe(df, use_container_width=True)
            st.markdown(f"### 🧾 Total Dispatch Value: ₹ {df['Total Amount'].sum():,.2f}")
        else:
            st.info("No dispatch data available.")

    except Exception as e:
        st.error(f"⚠️ Error loading reports: {e}")
    finally:
        conn.close()

    st.markdown("---")
    if st.button("⬅ Return to Main Menu", key="return_main_reports_btn"):
        st.session_state['page'] = 'Main Menu'
        st.rerun()

    if st.button("🔒 Logout", key="logout_reports_btn"):
        st.session_state.clear()
        st.rerun()

def sales_page(admin_view=False):
    show_header()
    st.markdown(f"### 👋 Welcome back, **{st.session_state.get('username', 'User')}**!")
    st.info("You're on the Sales Orders page.")

    username = st.session_state.get('username')
    conn = sqlite3.connect('orders.db')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # --- Upload buyer Excel file (Only Admin can replace it) ---
    if st.session_state['role'] == 'Admin':
        uploaded_file = st.file_uploader("Upload Buyer Excel File", type=["xlsx"])
        if uploaded_file is not None:
            with open("buyers.xlsx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ Buyer file uploaded and saved as 'buyers.xlsx'. Please refresh to see updates.")

    # --- Load buyer list from file ---
    buyer_df = None
    if os.path.exists("buyers.xlsx"):
        try:
            buyer_df = pd.read_excel("buyers.xlsx", engine="openpyxl")
            buyer_df.columns = buyer_df.columns.str.strip()
            buyer_names = buyer_df["Buyer Name"].dropna().unique().tolist()
        except Exception as e:
            st.warning(f"⚠️ Error reading buyers.xlsx: {e}")
            buyer_df = None
    else:
        st.info("📂 Buyer list not found. Please ask Admin to upload 'buyers.xlsx'.")

    # --- Buyer Details Form ---
    st.subheader("🧾 Buyer Details")
    customer_name = ""
    address = ""
    gstin = ""

    if buyer_df is not None:
        selected_buyer = st.selectbox("Select Buyer (or leave blank to enter manually)", [""] + buyer_names)
        if selected_buyer:
            buyer_row = buyer_df[buyer_df["Buyer Name"] == selected_buyer].iloc[0]
            customer_name = selected_buyer
            address = buyer_row["Address"]
            gstin = buyer_row["GSTIN/UIN"]

            st.markdown(f"**Address:** {address}")
            st.markdown(f"**GSTIN:** {gstin}")
        else:
            customer_name = st.text_input("Customer Name", key="manual_customer_name")
            address = st.text_area("Address", key="manual_address")
            gstin = st.text_input("GSTIN", key="manual_gstin")
    else:
        customer_name = st.text_input("Customer Name", key="manual_customer_name")
        address = st.text_area("Address", key="manual_address")
        gstin = st.text_input("GSTIN", key="manual_gstin")

    # --- Auto-generate Order Number ---
    c.execute("SELECT order_no FROM orders ORDER BY order_id DESC LIMIT 1")
    last_order = c.fetchone()
    if last_order:
        try:
            last_num = int(last_order[0].split('-')[-1])
        except:
            last_num = 0
    else:
        last_num = 0

    new_order_no = f"ORD-{last_num + 1:04d}"
    st.markdown(f"### 🆕 Auto-Generated Order Number: `{new_order_no}`")

    # --- Order Info ---
    order_no = new_order_no  # override text_input and use auto-generated value
    order_date = st.date_input("Order Date", datetime.today(), key="sales_order_date")
    urgent_flag = st.checkbox("Mark as Urgent", key="sales_urgent_flag")

    # --- Product Entry ---
    st.write("📦 Enter Products")
    unit_options = ["KG", "Nos"]
    currency_options = ["INR", "USD"]
    price_type_options = ["Per Kg", "Per Nos"]

    product_columns = ['Product Name', 'Quantity', 'Unit', 'Currency', 'Price', 'Price Type']
    product_data = pd.DataFrame(columns=product_columns)
    column_config = {
        "Unit": st.column_config.SelectboxColumn("Unit", options=unit_options),
        "Currency": st.column_config.SelectboxColumn("Currency", options=currency_options),
        "Price Type": st.column_config.SelectboxColumn("Price Type", options=price_type_options),
    }

    products = st.data_editor(product_data, column_config=column_config, num_rows="dynamic", key="sales_products_editor")

    if not products.empty and 'Quantity' in products.columns and 'Price' in products.columns:
        try:
            products['Quantity'] = pd.to_numeric(products['Quantity'], errors='coerce').fillna(0)
            products['Price'] = pd.to_numeric(products['Price'], errors='coerce').fillna(0)
            products['Total'] = products['Quantity'] * products['Price']
        except Exception as e:
            st.warning(f"Error calculating totals: {e}")
            products['Total'] = 0.0

    st.write("🔍 Order Summary Preview:")
    st.data_editor(products, use_container_width=True, key="summary_preview_editor")

    grand_total = 0.0
    if 'Total' in products:
        try:
            grand_total = products['Total'].astype(float).sum()
            st.markdown(f"### 🧾 Grand Total: ₹ {grand_total:,.2f}")
        except:
            pass

    # --- Submit Order ---
    if st.button("✅ Submit Order", key="sales_submit_order"):
        if not customer_name.strip():
            st.warning("Please fill in Customer Name.")
        elif products.empty or products['Product Name'].isnull().all():
            st.warning("Please enter at least one product.")
        else:
            try:
                c.execute('''
                    INSERT INTO orders (created_by, customer_name, order_no, order_date, urgent_flag, address, gstin)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, customer_name.strip(), order_no.strip(), str(order_date), int(urgent_flag), address.strip(), gstin.strip()))
                order_id = c.lastrowid

                for _, row in products.iterrows():
                    if row['Product Name']:
                        c.execute('''
                            INSERT INTO order_products (
                                order_id, product_name, quantity, unit, price_inr, price_usd, status
                            )
                            VALUES (?, ?, ?, ?, ?, ?, 'Original')
                        ''', (
                            order_id,
                            row['Product Name'],
                            row['Quantity'],
                            row['Unit'],
                            row['Price'] if row['Currency'] == "INR" else 0,
                            row['Price'] if row['Currency'] == "USD" else 0
                        ))

                conn.commit()
                st.success("✅ Order Created Successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving order: {e}")

    # --- Existing Orders List ---
    st.subheader("📋 My Orders")
    try:
        c.execute('''
            SELECT o.order_id, o.customer_name, o.order_no, o.order_date, o.urgent_flag, o.gstin
            FROM orders o
            WHERE o.created_by = ?
            ORDER BY o.order_date DESC
        ''', (username,))
        orders = c.fetchall()

        for order in orders:
            st.markdown(
                f"### Order No: {order[2]} | Customer: {order[1]} | GSTIN: {order[5]} | Date: {order[3]} | Urgent: {'Yes' if order[4] else 'No'}"
            )

            # Admin-only delete button after order summary
            if admin_view:
                if st.button(f"❌ Delete Order #{order[2]}", key=f"delete_order_{order[0]}"):
                    try:
                        c.execute("DELETE FROM order_products WHERE order_id = ?", (order[0],))
                        c.execute("DELETE FROM orders WHERE order_id = ?", (order[0],))
                        conn.commit()
                        st.success(f"✅ Order {order[2]} deleted successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting order: {e}")

            c.execute('''
                SELECT product_name, quantity, unit, price_inr, price_usd
                FROM order_products
                WHERE order_id = ? AND status = 'Original'
            ''', (order[0],))
            products = c.fetchall()
            df = pd.DataFrame(products, columns=['Product Name', 'Qty', 'Unit', 'Price INR', 'Price USD'])

            df['Total INR'] = df['Qty'] * df['Price INR']
            df['Total USD'] = df['Qty'] * df['Price USD']

            st.data_editor(df, disabled=True, use_container_width=True, key=f"view_table_{order[0]}")

            # Show grand totals
            total_inr = df['Total INR'].sum()
            total_usd = df['Total USD'].sum()
            st.markdown(f"**🧾 Grand Total INR:** ₹ {total_inr:,.2f} | **USD:** $ {total_usd:,.2f}")

    except Exception as e:
        st.error(f"⚠️ Error fetching orders: {e}")

    conn.close()
    return_menu_logout("sales")

def dispatch_page(admin_view=False):
    show_header()

    st.markdown(f"### 👋 Welcome back, **{st.session_state.get('username', 'User')}**!")
    st.info("You're on the Dispatch Page. View and dispatch orders below.")

    conn = sqlite3.connect('orders.db')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # --- Fetch all Orders ---
    c.execute("SELECT order_id, customer_name, order_no, order_date, urgent_flag FROM orders ORDER BY order_date DESC")
    orders = c.fetchall()

    for order in orders:
        order_id, customer_name, order_no, order_date, urgent_flag = order
        st.markdown(f"## Order No: {order_no} | Customer: {customer_name} | Date: {order_date} | Urgent: {'Yes' if urgent_flag else 'No'}")

        # Fetch Original Products
        c.execute('''
            SELECT product_name, quantity, unit, price_inr, price_usd
            FROM order_products
            WHERE order_id = ? AND status = 'Original'
        ''', (order_id,))
        original_products = pd.DataFrame(c.fetchall(), columns=['Product Name', 'Original Qty', 'Unit', 'Price INR', 'Price USD'])

        if original_products.empty:
            st.warning("No products found for this order.")
            continue

        st.markdown("### 📦 Original Order")
        st.dataframe(original_products, use_container_width=True)

        # Fetch Dispatched History
        c.execute('''
            SELECT product_name, quantity, unit, price_inr, price_usd
            FROM order_products
            WHERE order_id = ? AND status = 'Dispatched'
        ''', (order_id,))
        dispatched_products = pd.DataFrame(c.fetchall(), columns=['Product Name', 'Dispatched Qty', 'Unit', 'Price INR', 'Price USD'])

        if not dispatched_products.empty:
            st.markdown("### ✅ Dispatched History")
            st.dataframe(dispatched_products, use_container_width=True)

        # Show balance qty calculation
        st.markdown("### 📊 Balance Quantity")
        merged = original_products[['Product Name', 'Original Qty']].copy()
        if not dispatched_products.empty:
            dispatched_sum = dispatched_products.groupby('Product Name')['Dispatched Qty'].sum().reset_index()
            merged = pd.merge(merged, dispatched_sum, on='Product Name', how='left').fillna(0)
        else:
            merged['Dispatched Qty'] = 0

        merged['Balance Qty'] = merged['Original Qty'] - merged['Dispatched Qty']
        st.dataframe(merged, use_container_width=True)

        # Only allow dispatch if there is a balance quantity
        balance_df = merged[merged['Balance Qty'] > 0][['Product Name', 'Balance Qty']]
        if balance_df.empty:
            st.info("✅ Order fully dispatched.")
            continue

        st.markdown("### 🚚 Dispatch Entry")
        dispatch_df = pd.DataFrame(columns=['Product Name', 'Quantity', 'Unit', 'Currency', 'Price'])
        product_names = balance_df['Product Name'].tolist()
        column_config = {
            "Product Name": st.column_config.SelectboxColumn("Product Name", options=product_names),
            "Unit": st.column_config.SelectboxColumn("Unit", options=['KG', 'Nos']),
            "Currency": st.column_config.SelectboxColumn("Currency", options=['INR', 'USD'])
        }

        new_dispatch = st.data_editor(dispatch_df, column_config=column_config, num_rows='dynamic', key=f"dispatch_entry_{order_id}")

        if st.button("🚀 Submit Dispatch", key=f"submit_dispatch_{order_id}"):
            try:
                for _, row in new_dispatch.iterrows():
                    if row['Product Name'] and float(row['Quantity']) > 0:
                        qty_allowed = balance_df.loc[balance_df['Product Name'] == row['Product Name'], 'Balance Qty'].values[0]
                        if float(row['Quantity']) <= qty_allowed:
                            c.execute('''
                                INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status)
                                VALUES (?, ?, ?, ?, ?, ?, 'Dispatched')
                            ''', (
                                order_id,
                                row['Product Name'],
                                row['Quantity'],
                                row['Unit'],
                                row['Price'] if row['Currency'] == 'INR' else 0,
                                row['Price'] if row['Currency'] == 'USD' else 0
                            ))
                        else:
                            st.warning(f"❌ Quantity for {row['Product Name']} exceeds balance.")
                conn.commit()
                st.success("✅ Dispatch submitted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error submitting dispatch: {e}")

    conn.close()
    return_menu_logout("dispatch")

def admin_page():
    show_header()
    
    st.markdown(f"### 👋 Welcome back, **{st.session_state.get('username')}**!")
    st.info("You're on the Admin Panel.")

    os.makedirs("data", exist_ok=True)
    db_path = os.path.join("data", "users.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # --- Create users table only if not exists ---
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            full_name TEXT
        )
    ''')

    # --- Create New User ---
    st.subheader("➕ Create New User")
    new_username = st.text_input("Username", key="admin_new_username")
    new_password = st.text_input("Password", type="password", key="admin_new_password")
    new_role = st.selectbox("Role", ["Admin", "Sales", "Dispatch"], key="admin_new_role")
    new_full_name = st.text_input("Full Name", key="admin_new_fullname")

    if st.button("Create User", key="admin_create_user"):
        if not new_username.strip() or not new_password or not new_full_name.strip():
            st.warning("Please enter username, full name, and password.")
        else:
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            try:
                c.execute('''
                    INSERT INTO users (username, password_hash, role, full_name)
                    VALUES (?, ?, ?, ?)
                ''', (new_username.strip(), hashed_pw, new_role, new_full_name.strip()))
                conn.commit()
                st.success(f"✅ User '{new_username}' created successfully!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("⚠️ Username already exists.")

    # --- Manage Existing Users ---
    st.markdown("---")
    st.subheader("👥 Manage Existing Users")
    c.execute("SELECT user_id, username, role, full_name FROM users ORDER BY user_id")
    users = c.fetchall()

    for user_id, username, role, full_name in users:
        col1, col2, col3 = st.columns([3, 3, 4])
        with col1:
            st.markdown(f"**{username}**  \n_Full Name_: {full_name}  \n_Role_: {role}")
        with col2:
            updated_role = st.selectbox("Change Role", ["Admin", "Sales", "Dispatch"],
                                        index=["Admin", "Sales", "Dispatch"].index(role),
                                        key=f"role_{user_id}")
            if updated_role != role:
                if st.button("Update Role", key=f"update_role_{user_id}"):
                    c.execute("UPDATE users SET role = ? WHERE user_id = ?", (updated_role, user_id))
                    conn.commit()
                    st.success(f"✅ Role updated for '{username}' to {updated_role}")
                    st.rerun()
        with col3:
            new_pw = st.text_input(f"New Password for {username}", type="password", key=f"new_pw_{user_id}")
            if new_pw:
                if st.button("Reset Password", key=f"reset_pw_{user_id}"):
                    hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
                    c.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (hashed_pw, user_id))
                    conn.commit()
                    st.success(f"🔐 Password reset for '{username}'")
                    st.rerun()

    # --- Change My Password (Admin) ---
    if st.session_state['role'] == "Admin":
        st.markdown("---")
        st.subheader("🔐 Change My Password")
        current_user = st.session_state['username']
        new_pw = st.text_input("New Password", type="password", key="admin_change_own_pw")
        if new_pw:
            if st.button("Update My Password", key="update_own_pw"):
            hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
            c.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_pw, current_user))
            conn.commit()
            st.success("✅ Your password has been updated.")

            if username != "admin":
                if st.button("❌ Delete", key=f"delete_{user_id}"):
                    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                    conn.commit()
                    st.warning(f"🗑️ User '{username}' deleted.")
                    st.rerun()

    conn.close()
    st.markdown("---")
    return_menu_logout("admin")

def main_app():
    st.sidebar.write("📁 DB Path:")
    st.sidebar.write(os.path.abspath("orders.db"))
    st.sidebar.title("Navigation")
    if st.session_state['role'] == 'Admin':
        page = st.sidebar.radio("Go to", ["Admin", "Sales Orders", "Dispatch", "Reports"])
    elif st.session_state['role'] == 'Sales':
        page = st.sidebar.radio("Go to", ["Sales Orders"])
    elif st.session_state['role'] == 'Dispatch':
        page = st.sidebar.radio("Go to", ["Dispatch", "Reports"])
    else:
        page = "Invalid Role"

    if page == "Admin":
        admin_page()
    elif page == "Sales Orders":
        sales_page()
    elif page == "Dispatch":
        dispatch_page()
    elif page == "Reports":
        reports_page()

if __name__ == '__main__':
    st.set_page_config(page_title="Order Management", layout="wide")
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Main Menu'
        
    if not st.session_state['logged_in']:
        login_page()
    else:
        if st.session_state['page'] == 'Main Menu':
            main_menu()
        elif st.session_state['page'] == 'Admin Panel':
            admin_page()
        elif st.session_state['page'] == 'Dispatch':
            dispatch_page(admin_view=True)
        elif st.session_state['page'] == 'Orders':
            sales_page(admin_view=True)
        elif st.session_state['page'] == 'Reports':
            reports_page()








