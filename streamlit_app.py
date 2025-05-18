import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def show_header():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("assets/logo.jpg", width=140)
    with col2:
        st.markdown("## Shree Sai Salt - Order Management")

def return_menu_logout(key_prefix):
    st.markdown("---")
    if st.button("⬅ Return to Main Menu", key=f"return_main_{key_prefix}"):
        st.session_state['page'] = 'Main Menu'
    if st.button("🔒 Logout", key=f"logout_{key_prefix}"):
        st.session_state['logged_in'] = False
        st.rerun()

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
    show_header()
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info("You're viewing Reports and Analysis.")

    # Connect DB
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()

    # --- Max Demand Product ---
    st.subheader("Max Demand Product (By Ordered Quantity)")
    c.execute('''
        SELECT product_name, SUM(quantity) as total_qty
        FROM order_products
        WHERE status = 'Original'
        GROUP BY product_name
        ORDER BY total_qty DESC
        LIMIT 1
    ''')
    result = c.fetchone()
    if result:
        st.success(f"Highest Demand: {result[0]} with {result[1]} units")
    else:
        st.warning("No data available.")

    # --- Min Demand Product ---
    st.subheader("Min Demand Product (Excluding Zero)")
    c.execute('''
        SELECT product_name, SUM(quantity) as total_qty
        FROM order_products
        WHERE status = 'Original'
        GROUP BY product_name
        HAVING total_qty > 0
        ORDER BY total_qty ASC
        LIMIT 1
    ''')
    result = c.fetchone()
    if result:
        st.info(f"Lowest Demand: {result[0]} with {result[1]} units")
    else:
        st.warning("No data available.")

    # --- Sales Graph ---
    st.subheader("Sales Graph (By Quantity and Amount)")
    view_by = st.selectbox("View By", ["Quantity", "Amount INR", "Amount USD"], key="reports_view_by")

    if view_by == "Quantity":
        c.execute('''
            SELECT product_name, SUM(quantity)
            FROM order_products
            WHERE status IN ('Original', 'Dispatched')
            GROUP BY product_name
        ''')
    elif view_by == "Amount INR":
        c.execute('''
            SELECT product_name, SUM(quantity * price_inr)
            FROM order_products
            WHERE status IN ('Original', 'Dispatched')
            GROUP BY product_name
        ''')
    else:
        c.execute('''
            SELECT product_name, SUM(quantity * price_usd)
            FROM order_products
            WHERE status IN ('Original', 'Dispatched')
            GROUP BY product_name
        ''')

    data = c.fetchall()
    if data:
        df = pd.DataFrame(data, columns=['Product Name', 'Total'])
        fig, ax = plt.subplots()
        df.set_index('Product Name')['Total'].plot(kind='bar', ax=ax)
        ax.set_ylabel(view_by)
        st.pyplot(fig)
    else:
        st.warning("No data to display.")

    conn.close()

    # Return menu and logout (always at the end)
    return_menu_logout("reports")

def sales_page(admin_view=False):
    show_header()
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info("You're on the Sales Orders page.")

    username = st.session_state['username']

    # Connect DB
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()

    # --- New Order Form ---
    st.subheader("Create New Order")
    customer_name = st.text_input("Customer Name", key="sales_customer_name")
    order_no = st.text_input("Order Number", key="sales_order_no")
    order_date = st.date_input("Order Date", datetime.today(), key="sales_order_date")
    urgent_flag = st.checkbox("Mark as Urgent", key="sales_urgent_flag")

    # Multi-product entry
    st.write("Enter Products")
    products = st.data_editor(pd.DataFrame(columns=['Product Name', 'Quantity', 'Unit', 'Price INR', 'Price USD']),
                              num_rows="dynamic", key="sales_products_editor")

    if st.button("Submit Order", key="sales_submit_order"):
        c.execute('INSERT INTO orders (created_by, customer_name, order_no, order_date, urgent_flag) VALUES (?, ?, ?, ?, ?)',
                  (username, customer_name, order_no, str(order_date), int(urgent_flag)))
        order_id = c.lastrowid
        for _, row in products.iterrows():
            if row['Product Name']:
                c.execute('''
                    INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Original')
                ''', (order_id, row['Product Name'], row['Quantity'], row['Unit'], row['Price INR'], row['Price USD']))
        conn.commit()
        st.success("Order Created Successfully!")

    # --- Existing Orders List ---
    st.subheader("My Orders")
    c.execute('''
        SELECT o.order_id, o.customer_name, o.order_no, o.order_date, o.urgent_flag
        FROM orders o
        WHERE o.created_by = ?
        ORDER BY o.order_date DESC
    ''', (username,))
    orders = c.fetchall()

    for order in orders:
        st.markdown(f"### Order No: {order[2]} | Customer: {order[1]} | Date: {order[3]} | Urgent: {'Yes' if order[4] else 'No'}")

        # Fetch products
        c.execute('''
            SELECT order_product_id, product_name, quantity, unit, price_inr, price_usd, status
            FROM order_products
            WHERE order_id = ?
        ''', (order[0],))
        products = c.fetchall()
        df = pd.DataFrame(products, columns=['ID', 'Product Name', 'Qty', 'Unit', 'Price INR', 'Price USD', 'Status'])
        st.dataframe(df)

        # Option to edit
        st.write("Edit Products:")
        edited = st.data_editor(df[['Product Name', 'Qty', 'Unit', 'Price INR', 'Price USD']],
                                num_rows="dynamic", key=f"sales_edit_{order[0]}")
        if st.button(f"Save Edits for Order {order[2]}", key=f"sales_save_edit_{order[0]}"):
            for idx, row in edited.iterrows():
                # Insert edited version as new record with 'Edited' status
                c.execute('''
                    INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status, modified_by, modified_date)
                    VALUES (?, ?, ?, ?, ?, ?, 'Edited', ?, ?)
                ''', (order[0], row['Product Name'], row['Qty'], row['Unit'], row['Price INR'], row['Price USD'], username, str(datetime.now())))
            conn.commit()
            st.success("Edits saved! Both original and edited will be visible.")

    conn.close()

    # Return menu and logout (always at the end)
    return_menu_logout("sales")

def dispatch_page(admin_view=False):
    show_header()
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info("You're on the Dispatch Management page.")

    username = st.session_state['username']

    # Connect DB
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()

    # --- Show Pending & Urgent Orders (FIFO unless urgent) ---
    st.subheader("Pending & Urgent Orders")
    c.execute('''
        SELECT o.order_id, o.customer_name, o.order_no, o.order_date, o.urgent_flag
        FROM orders o
        WHERE o.order_id NOT IN (
            SELECT DISTINCT order_id FROM order_products WHERE status = 'Dispatched'
        )
        ORDER BY o.urgent_flag DESC, o.order_date ASC
    ''')
    orders = c.fetchall()

    for order in orders:
        st.markdown(f"### Order No: {order[2]} | Customer: {order[1]} | Date: {order[3]} | Urgent: {'Yes' if order[4] else 'No'}")

        # Fetch products
        c.execute('''
            SELECT order_product_id, product_name, quantity, unit, price_inr, price_usd, status
            FROM order_products
            WHERE order_id = ? AND status = 'Original'
        ''', (order[0],))
        products = c.fetchall()
        df = pd.DataFrame(products, columns=['Order Product ID', 'Product Name', 'Qty', 'Unit', 'Price INR', 'Price USD', 'Status'])
        st.dataframe(df)

        # Dispatch Editor
        st.write("Dispatch These Products (Adjust Qty if needed):")
        dispatch_df = st.data_editor(df[['Product Name', 'Qty', 'Unit']], num_rows="dynamic", key=f"dispatch_editor_{order[0]}")
        remarks = st.text_input(f"Remarks for Order {order[2]}", key=f"remarks_{order[0]}")

        if st.button(f"Mark Dispatched Order {order[2]}", key=f"dispatch_mark_{order[0]}"):
            for idx, row in dispatch_df.iterrows():
                c.execute('''
                    INSERT INTO order_products (order_id, product_name, quantity, unit, price_inr, price_usd, status, modified_by, modified_date)
                    VALUES (?, ?, ?, ?, 0, 0, 'Dispatched', ?, ?)
                ''', (order[0], row['Product Name'], row['Qty'], row['Unit'], username, str(datetime.now())))
            conn.commit()
            st.success(f"Order {order[2]} marked as Dispatched. Both versions now visible.")
            st.rerun()

    # --- Show Dispatched Orders ---
    st.subheader("Dispatched Orders")
    c.execute('''
        SELECT DISTINCT o.order_id, o.customer_name, o.order_no, o.order_date
        FROM orders o
        JOIN order_products op ON o.order_id = op.order_id
        WHERE op.status = 'Dispatched'
        ORDER BY o.order_date DESC
    ''')
    dispatched_orders = c.fetchall()

    for order in dispatched_orders:
        st.markdown(f"### Order No: {order[2]} | Customer: {order[1]} | Date: {order[3]}")

        # Show original & dispatched products
        c.execute('''
            SELECT product_name, quantity, unit, status, modified_by, modified_date
            FROM order_products
            WHERE order_id = ?
        ''', (order[0],))
        products = c.fetchall()
        df = pd.DataFrame(products, columns=['Product Name', 'Qty', 'Unit', 'Status', 'Modified By', 'Modified Date'])
        st.dataframe(df)

    conn.close()

    # Return menu and logout (always at the end)
    return_menu_logout("dispatch")

def admin_page():
    show_header()
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info("You're on the Admin Panel.")
    ...

    st.subheader("➕ Create New User")
    new_username = st.text_input("Username", key="admin_new_username")
    new_password = st.text_input("Password", type="password", key="admin_new_password")
    new_role = st.selectbox("Role", ["Admin", "Sales", "Dispatch"], key="admin_new_role")

    if st.button("Create User", key="admin_create_user"):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        try:
            c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      (new_username, hashed_pw, new_role))
            conn.commit()
            st.success(f"User '{new_username}' created successfully! Password: {new_password}")
        except sqlite3.IntegrityError:
            st.error("⚠️ Username already exists.")
        conn.close()
        st.rerun()

    st.markdown("---")
    st.subheader("👥 Manage Existing Users")

    # Load users WITH password hash
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, role FROM users ORDER BY user_id")
    users = c.fetchall()

    for user_id, username, role in users:
        col1, col2, col3 = st.columns([3, 3, 4])

        # --- Column 1: User Info ---
        with col1:
            st.markdown(f"**{username}**  \n_Role_: {role}")

        # --- Column 2: Role Editor ---
        with col2:
            new_role = st.selectbox("Change Role", ["Admin", "Sales", "Dispatch"],
                                    index=["Admin", "Sales", "Dispatch"].index(role),
                                    key=f"role_{user_id}")
            if new_role != role:
                if st.button("Update Role", key=f"update_role_{user_id}"):
                    c.execute("UPDATE users SET role = ? WHERE user_id = ?", (new_role, user_id))
                    conn.commit()
                    st.success(f"Role updated for {username} to {new_role}")
                    st.rerun()

        # --- Column 3: Reset Password & Delete ---
        with col3:
            new_pw = st.text_input(f"New Password for {username}", type="password", key=f"new_pw_{user_id}")
            if new_pw:
                if st.button("Reset Password", key=f"reset_pw_{user_id}"):
                    hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
                    c.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (hashed_pw, user_id))
                    conn.commit()
                    st.success(f"Password reset for '{username}' to: {new_pw}")
                    st.rerun()

            if username != "admin":
                if st.button("❌ Delete", key=f"delete_{user_id}"):
                    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                    conn.commit()
                    st.warning(f"User '{username}' deleted.")
                    st.rerun()

    conn.close()
    return_menu_logout("admin")

def main_app():
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




