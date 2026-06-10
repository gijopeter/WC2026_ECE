import streamlit as st
import hashlib
from modules.config import ADMIN_PASSWORD_HASH  # make sure config.py is in modules

def login():
    """Render admin login form"""
    st.subheader("Admin Login")

    with st.form("login_form"):
        password = st.text_input("Enter Admin Password", type="password", key="login_password")
        submitted = st.form_submit_button("🔑 Login", use_container_width=True)

        if submitted:
            entered_hash = hashlib.sha256(password.encode()).hexdigest()
            if entered_hash == ADMIN_PASSWORD_HASH:
                st.session_state.admin_authenticated = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Incorrect password")


def logout():
    """Render logout button for admin"""
    if st.button("🚪 Logout", key="logout_button"):
        st.session_state.admin_authenticated = False
        st.session_state.admin_page = "home"
        st.rerun()