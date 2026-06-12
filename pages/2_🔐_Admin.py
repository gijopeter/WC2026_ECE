
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from modules.auth import login, logout
from modules.admin_dashboard import show_dashboard
from modules.manage_players import manage_players
from modules.manage_games import manage_games
from modules.manage_polls_dashboard import manage_polls_dashboard
from modules.manage_questions import manage_questions
from modules.manage_options import manage_options
from modules.results import manage_results
from modules.pdf_reports import generate_pdf_reports
from modules.export_snapshot import export_snapshot

from modules.database import *
init_db()

# Session init
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "admin_page" not in st.session_state:
    st.session_state.admin_page = "home"

# Styling
st.markdown("""
<style>
div.stButton > button {
    height: 100px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("🔐 Admin Panel")

# Authentication
if not st.session_state.admin_authenticated:
    login()
else:
    logout()

    page = st.session_state.admin_page

    if page == "home":
        show_dashboard()

    elif page == "players":
        manage_players()

    elif page == "games":
        manage_games()

    elif page == "polls":
        manage_polls_dashboard()

    elif page == "poll_questions":
        manage_questions()

    elif page == "poll_options":
        manage_options()

    elif page == "poll_selections":
        from modules.selections import manage_selections
        manage_selections()

    elif page == "poll_results":
        manage_results()

    elif st.session_state.admin_page == "pdf_reports":
        generate_pdf_reports()      

    elif st.session_state.admin_page == "export_snapshot":
        export_snapshot()        