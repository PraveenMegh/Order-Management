import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Header with Logo and App Name ---
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

# --- Return Buttons for all Pages ---
def return_menu_logout(key_prefix):
    st.markdown("---")
    if st.button("⬅ Return to Main Menu", key=f"return_main_{key_prefix}"):
        st.session_state['page'] = 'Main Menu'
    if st.button("🔒 Logout", key=f"logout_{key_prefix}"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- Login Page ---
def login_page():
    show_header()
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
    st.title("📊 Reports and Analytics")
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info("Track demand, dispatched summary, and performance insights.")

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    # --- Max Demand Product ---
    st.subheader("🔥 Highest Demand Product")
    c.execute('''
        SELECT product_name, SUM(bags) as total_bags, SUM(quantity) as total_kg
        FROM order_products
        WHERE status = 'Original'
        GROUP BY product_name
        ORDER BY total_kg DESC
        LIMIT 1
    ''')
    result = c.fetchone()
    if result:
        st.success(f"Max Demand: {result[0]} | Bags: {result[1]} | Total KG: {result[2]}")
    else:
        st.warning("No order data available.")

    # --- Min Demand Product ---
    st.subheader("💤 Lowest Demand Product")
    c.execute('''
        SELECT product_name, SUM(bags) as total_bags, SUM(quantity) as total_kg
        FROM order_products
        WHERE status = 'Original'
        GROUP BY product_name
        HAVING SUM(quantity) > 0
        ORDER BY total_kg ASC
        LIMIT 1
    ''')
    result = c.fetchone()
    if result:
        st.info(f"Min Demand: {result[0]} | Bags: {result[1]} | Total KG: {result[2]}")
    else:
        st.warning("No order data available.")

    # --- Demand Chart ---
    st.subheader("📈 Product Demand Chart")
    view_option = st.selectbox("View By", ["Total Bags", "Total KG", "Amount (INR)"])

    if view_option == "Total Bags":
        c.execute('''
            SELECT product_name, SUM(bags)
            FROM order_products
            WHERE status IN ('Original', 'Dispatched')
            GROUP BY product_name
        ''')
    elif view_option == "Total KG":
        c.execute('''
            SELECT product_name, SUM(quantity)
            FROM order_products
            WHERE status IN ('Original', 'Dispatched')
            GROUP BY product_name
        ''')
    else:
        c.execute('''
            SELECT product_name, SUM(total_price)
            FROM order_products
            WHERE status IN ('Original', 'Dispatched')
            GROUP BY product_name
        ''')

    data = c.fetchall()
    if data:
        df = pd.DataFrame(data, columns=["Product", "Value"])
        fig, ax = plt.subplots()
        df.set_index("Product")["Value"].plot(kind="bar", ax=ax)
        ax.set_ylabel(view_option)
        ax.set_title(f"Product-wise {view_option}")
        st.pyplot(fig)
    else:
        st.warning("No data to display.")

    # --- Dispatched Summary ---
    st.subheader("🚚 Dispatch Summary")
    c.execute('''
        SELECT product_name, SUM(quantity) AS dispatched_kg
        FROM order_products
        WHERE status = 'Dispatched'
        GROUP BY product_name
    ''')
    dispatched = c.fetchall()

    if dispatched:
        st.dataframe(pd.DataFrame(dispatched, columns=["Product", "Dispatched KG"]))
    else:
        st.info("No dispatch data available.")

    conn.close()

    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# --- Orders Page Function ---
def orders_page():
    st.title("📝 Order Entry")
    st.markdown(f"### 👋 Welcome, **{st.session_state['username']}**!")
    st.info("Create and manage your orders.")

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()

    username = st.session_state['username']
    role = st.session_state['role']

    # --- Create New Order ---
    st.subheader("➕ Create New Order")
    customer_name = st.text_input("Customer Name")
    order_date = st.date_input("Order Date", value=datetime.today())
    urgent_flag = st.checkbox("Mark as Urgent")

    st.markdown("---")
    st.markdown("### 📦 Add Products")

    bag_sizes = [25, 30, 40, 50]
    product_data = []
    num_products = st.number_input("Number of Products", min_value=1, max_value=20, value=1)

    for i in range(num_products):
        st.markdown(f"#### Product {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.text_input(f"Product Name {i+1}", key=f"pname_{i}")
            rate = st.number_input(f"Rate per KG {i+1}", min_value=0.0, step=0.5, key=f"rate_{i}")
        with col2:
            bag_size = st.selectbox(f"Bag Size (KG) {i+1}", options=bag_sizes, key=f"bsize_{i}")
            bags = st.number_input(f"No. of Bags {i+1}", min_value=1, key=f"bags_{i}")
        with col3:
            total_qty = bag_size * bags
            total_price = total_qty * rate
            st.markdown(f"**Total KG**: {total_qty} KG")
            st.markdown(f"**Total Price**: ₹{total_price:.2f}")
        if product_name:
            product_data.append((product_name, bag_size, bags, total_qty, rate, total_price))

    # --- Submit Order ---
    if st.button("✅ Submit Order"):
        if not customer_name or not product_data:
            st.warning("Please fill in all required fields and at least one product.")
        else:
            c.execute('''
                INSERT INTO orders (created_by, customer_name, order_date, urgent_flag)
                VALUES (?, ?, ?, ?)
            ''', (username, customer_name, str(order_date), int(urgent_flag)))
            order_id = c.lastrowid
            for p in product_data:
                c.execute('''
                    INSERT INTO order_products (order_id, product_name, bag_size_kg, bags, quantity, rate_inr, total_price, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'Original')
                ''', (order_id, p[0], p[1], p[2], p[3], p[4], p[5]))
            conn.commit()
            st.success(f"✅ Order #{order_id} created successfully!")
            st.rerun()

    # --- View Orders ---
    st.subheader("📋 My Orders")
    if role == 'Admin':
        c.execute('''
            SELECT o.order_id, o.customer_name, o.order_date, o.urgent_flag, o.created_by
            FROM orders o
            ORDER BY o.order_date DESC
        ''')
    else:
        c.execute('''
            SELECT o.order_id, o.customer_name, o.order_date, o.urgent_flag, o.created_by
            FROM orders o
            WHERE o.created_by = ?
            ORDER BY o.order_date DESC
        ''', (username,))

    all_orders = c.fetchall()
    for order in all_orders:
        st.markdown(f"### Order #{order[0]} | Customer: {order[1]} | Date: {order[2]} | Urgent: {'Yes' if order[3] else 'No'}")
        c.execute('''
            SELECT product_name, bag_size_kg, bags, quantity, rate_inr, total_price
            FROM order_products
            WHERE order_id = ? AND status = 'Original'
        ''', (order[0],))
        items = c.fetchall()
        df = pd.DataFrame(items, columns=['Product', 'Bag Size', 'Bags', 'Total KG', 'Rate (INR)', 'Total Price'])
        grand_total = df['Total Price'].sum()
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Grand Total:** ₹{grand_total:.2f}")

        if role == 'Admin':
            if st.button(f"❌ Delete Order #{order[0]}", key=f"delete_{order[0]}"):
                c.execute("DELETE FROM order_products WHERE order_id = ?", (order[0],))
                c.execute("DELETE FROM orders WHERE order_id = ?", (order[0],))
                conn.commit()
                st.warning(f"Order #{order[0]} deleted.")
                st.rerun()

    conn.close()

    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# --- Dispatch Page Function ---
def dispatch_page():
    st.title("🚚 Dispatch Management")
    st.markdown(f"### 👋 Welcome, **{st.session_state['username']}**!")

    conn = sqlite3.connect("orders.db")
    c = conn.cursor()
    username = st.session_state['username']

    # --- Fetch Pending Orders ---
    st.subheader("📦 Pending Orders")
    c.execute('''
        SELECT DISTINCT o.order_id, o.customer_name, o.order_date, o.urgent_flag
        FROM orders o
        JOIN order_products op ON o.order_id = op.order_id
        WHERE o.order_id NOT IN (
            SELECT order_id FROM order_products WHERE status = 'Dispatched'
        )
        ORDER BY o.urgent_flag DESC, o.order_date ASC
    ''')
    pending_orders = c.fetchall()

    for order in pending_orders:
        st.markdown(f"#### Order #{order[0]} | {order[1]} | Date: {order[2]} | Urgent: {'🔥 Yes' if order[3] else 'No'}")

        # Use 'Edited' if available, else 'Original'
        c.execute('SELECT status FROM order_products WHERE order_id = ? GROUP BY status', (order[0],))
        statuses = [s[0] for s in c.fetchall()]
        use_status = 'Edited' if 'Edited' in statuses else 'Original'

        c.execute('''
            SELECT order_product_id, product_name, bag_size_kg, bags, quantity, rate_inr
            FROM order_products
            WHERE order_id = ? AND status = ?
        ''', (order[0], use_status))
        products = c.fetchall()
        df = pd.DataFrame(products, columns=['ID', 'Product', 'Bag Size', 'Bags', 'Total KG', 'Rate'])
        df['Total Price'] = df['Total KG'] * df['Rate']
        st.dataframe(df, use_container_width=True)

        # Editable Quantity
        st.write("✏️ Adjust quantities before dispatch (if required):")
        editable_df = st.data_editor(df[['Product', 'Bag Size', 'Bags']], num_rows="dynamic", key=f"dispatch_editor_{order[0]}")

        if st.button(f"✅ Mark Order #{order[0]} as Dispatched", key=f"dispatch_btn_{order[0]}"):
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for _, row in editable_df.iterrows():
                total_qty = row['Bag Size'] * row['Bags']
                c.execute('''
                    INSERT INTO order_products (
                        order_id, product_name, bag_size_kg, bags, quantity, rate_inr, total_price, status, modified_by, modified_date
                    ) VALUES (?, ?, ?, ?, ?, 0, 0, 'Dispatched', ?, ?)
                ''', (
                    order[0], row['Product'], row['Bag Size'], row['Bags'], total_qty,
                    username, now
                ))
            conn.commit()
            st.success(f"✅ Order #{order[0]} marked as dispatched.")
            st.rerun()

    # --- Show Dispatched Orders ---
    st.markdown("---")
    st.subheader("✅ Dispatched Orders")
    c.execute('''
        SELECT DISTINCT o.order_id, o.customer_name, o.order_date
        FROM orders o
        JOIN order_products op ON o.order_id = op.order_id
        WHERE op.status = 'Dispatched'
        ORDER BY o.order_date DESC
    ''')
    dispatched = c.fetchall()

    for order in dispatched:
        st.markdown(f"### Order #{order[0]} | Customer: {order[1]} | Date: {order[2]}")
        c.execute('''
            SELECT product_name, bag_size_kg, bags, quantity, modified_by, modified_date
            FROM order_products
            WHERE order_id = ? AND status = 'Dispatched'
        ''', (order[0],))
        df = pd.DataFrame(c.fetchall(), columns=['Product', 'Bag Size', 'Bags', 'Total KG', 'Dispatched By', 'Dispatched On'])
        st.dataframe(df, use_container_width=True)

    conn.close()

    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# --- Admin Page Function ---
def admin_page():
    if "username" not in st.session_state or st.session_state.get("role") != "Admin":
        st.error("⛔ Access denied. Only Admins can access this page.")
        return

    st.title("🔧 Admin Panel")
    st.markdown(f"### 👋 Welcome back, **{st.session_state['username']}**!")
    st.info("You're on the Admin Panel.")

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
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            try:
                c.execute('''
                    INSERT INTO users (username, password_hash, role, full_name)
                    VALUES (?, ?, ?, ?)
                ''', (new_username.strip(), hashed_pw, new_role, new_full_name.strip()))
                conn.commit()
                st.success(f"✅ User '{new_username}' ({new_full_name}) created successfully!")
            except sqlite3.IntegrityError:
                st.error("⚠️ Username already exists.")
            conn.close()
            st.rerun()

    # --- Existing Users Section ---
    st.markdown("---")
    st.subheader("👥 Manage Existing Users")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username, role, full_name FROM users ORDER BY user_id")
    users = c.fetchall()

    for user_id, username, role, full_name in users:
        col1, col2, col3 = st.columns([3, 3, 4])

        with col1:
            st.markdown(f"**{username}**  \n_Full Name_: {full_name}  \n_Role_: {role}")

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

        with col3:
            new_pw = st.text_input(f"New Password for {username}", type="password", key=f"new_pw_{user_id}")
            if new_pw:
                if st.button("Reset Password", key=f"reset_pw_{user_id}"):
                    hashed_pw = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
                    c.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (hashed_pw, user_id))
                    conn.commit()
                    st.success(f"Password reset for '{username}'")
                    st.rerun()

            if username != "admin":
                if st.button("❌ Delete", key=f"delete_{user_id}"):
                    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                    conn.commit()
                    st.warning(f"User '{username}' deleted.")
                    st.rerun()

    conn.close()

    st.markdown("---")
    if st.button("🔒 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")

# Main Menu Navigator
def main_menu():
    st.sidebar.title("Navigation")
    role = st.session_state.get("role", "")
    
    if role == "Admin":
        page = st.sidebar.radio("Go to", ["Admin", "Sales Orders", "Dispatch", "Reports"])
    elif role == "Sales":
        page = st.sidebar.radio("Go to", ["Sales Orders"])
    elif role == "Dispatch":
        page = st.sidebar.radio("Go to", ["Dispatch", "Reports"])
    else:
        st.error("⛔ Invalid role.")
        return

    if page == "Admin":
        admin_page()
    elif page == "Sales Orders":
        orders_page(admin_view=False)
    elif page == "Dispatch":
        dispatch_page(admin_view=False)
    elif page == "Reports":
        reports_page()

# Entry point
if __name__ == '__main__':
    st.set_page_config(page_title="Order Management", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Main Menu'

    if not st.session_state['logged_in']:
        login_page()  # Your login logic here
    else:
        page = st.session_state['page']
        if page == 'Main Menu':
            main_menu()
        elif page == 'Admin Panel':
            admin_page()
        elif page == 'Dispatch':
            dispatch_page(admin_view=True)
        elif page == 'Orders':
            orders_page(admin_view=True)
        elif page == 'Reports':
            reports_page()
