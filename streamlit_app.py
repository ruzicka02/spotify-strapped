import time

import streamlit as st

if __name__ == "__main__":
    dashboard_page = st.Page("st_pages/dashboard.py", title="Dashboard")
    login_page = st.Page("st_pages/login.py", title="Login")
    pg = st.navigation([dashboard_page, login_page], expanded=False)
    pg.run()
