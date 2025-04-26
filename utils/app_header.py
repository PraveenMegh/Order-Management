import streamlit as st
from utils.app_header import show_header

def show_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image("assets/logo.jpg", width=120)
    with col2:
        st.markdown("""
            <div style='display: flex; align-items: center; height: 100%;'>
                <h2 style='margin: 0; padding-left: 10px;'>Shree Sai Industries</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin-top: 10px;'>", unsafe_allow_html=True)