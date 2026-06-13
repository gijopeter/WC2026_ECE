import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from modules.database import init_db
from modules.volunteer_auth import volunteer_login, volunteer_logout
from modules.selections import manage_selections

init_db()

st.title("📝 Volunteer Entry")

if "volunteer_authenticated" not in st.session_state:
    st.session_state.volunteer_authenticated = False

if "volunteer_username" not in st.session_state:
    st.session_state.volunteer_username = None

if not st.session_state.volunteer_authenticated:
    volunteer_login()
else:
    st.success(f"Logged in as: {st.session_state.volunteer_username}")
    volunteer_logout()

    manage_selections(
        volunteer_username=st.session_state.volunteer_username,
        show_back_button=False
    )