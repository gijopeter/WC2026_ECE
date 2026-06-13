import streamlit as st

def show_dashboard():

    st.markdown("## ⚙️ Admin Dashboard")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

    # ---------------- Row 1 ----------------
    with col1:
        if st.button("👤 Manage Players", use_container_width=True):
            st.session_state.admin_page = "players"

    with col2:
        if st.button("🏟 Manage Games", use_container_width=True):
            st.session_state.admin_page = "games"

    # ---------------- Row 2 ----------------
    with col3:
        if st.button("🗳 Manage Polls", use_container_width=True):
            st.session_state.admin_page = "polls"

    with col4:
        if st.button("📄 Generate PDF Reports", use_container_width=True):
            st.session_state.admin_page = "pdf_reports"

    # ---------------- Row 3 ----------------
    with col5:
        if st.button("📊 View Leaderboard", use_container_width=True):
            st.switch_page("pages/1_🏆_Leaderboard.py")

    with col6:
        if st.button("📤 Export Snapshot", use_container_width=True):
            st.session_state.admin_page = "export_snapshot"

    with col6:
        st.empty()