import streamlit as st
import os

def show_header():
    # --- Use relative asset path ---
    logo_path = os.path.join("assets", "logo.jpg")

    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.warning("⚠️ Logo not found. Please ensure 'assets/logo.jpg' exists.")

    st.title("Shree Sai Industries - Order Management System")
    st.markdown("---")
