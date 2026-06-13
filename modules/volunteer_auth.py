import streamlit as st
import hashlib

VOLUNTEERS = {
    "Sooraj": hashlib.sha256("SoorajA2D".encode()).hexdigest(),
    "volunteer2": hashlib.sha256("pass456".encode()).hexdigest(),
}


def volunteer_login():
    st.subheader("Volunteer Login")

    with st.form("volunteer_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            if username in VOLUNTEERS and VOLUNTEERS[username] == password_hash:
                st.session_state.volunteer_authenticated = True
                st.session_state.volunteer_username = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")


def volunteer_logout():
    if st.button("Logout"):
        st.session_state.volunteer_authenticated = False
        st.session_state.volunteer_username = None
        st.rerun()