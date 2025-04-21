import streamlit as st

def show_header():
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
        <img src='assets/logo.png' width='120'>
        <h2>Shree Sai Industries</h2>
    </div><hr>
    """, unsafe_allow_html=True)