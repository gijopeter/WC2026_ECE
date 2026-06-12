import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from modules.database import init_db
from modules.selections import manage_selections

init_db()

st.title("📝 Volunteer Entry")

st.info("Use this page to enter WhatsApp poll selections.")

manage_selections()