import streamlit as st
from utils.header import show_header
show_header()
from utils.auth import check_login
from PIL import Image

st.set_page_config(page_title='Order Management', layout='wide')

# Branding
st.markdown("""<div style='display:flex;align-items:center;gap:10px'>
<img src='https://via.placeholder.com/120x40.png?text=Shree+Sai+Salt' alt='Logo'>
<h2>Shree Sai Salt - Order Management</h2>
</div><hr>""", unsafe_allow_html=True)

check_login()  # Login check placeholder
st.sidebar.success("Select a page to continue.")