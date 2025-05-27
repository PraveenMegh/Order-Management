import streamlit as st
from datetime import datetime

def main_menu():
    st.markdown("## 🏠 Main Menu")
    st.markdown("Welcome to the Shree Sai Salt Order Management System.")
    st.markdown(f"📅 Today: {datetime.today().strftime('%B %d, %Y')}")

    st.markdown("Choose an option from the sidebar to begin.")
