import streamlit as st

def manage_polls_dashboard():

    st.markdown("## 🗳 Manage Polls")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

    # Row 1
    with col1:
        if st.button("❓ Poll Questions", use_container_width=True):
            st.session_state.admin_page = "poll_questions"

    with col2:
        if st.button("🎯 Poll Options & Points", use_container_width=True):
            st.session_state.admin_page = "poll_options"

    # Row 2
    with col3:
        if st.button("🗳 Enter User Selections", use_container_width=True):
            st.session_state.admin_page = "poll_selections"

    with col4:
        if st.button("🏆 Enter Match Results", use_container_width=True):
            st.session_state.admin_page = "poll_results"

    # Row 3
    with col5:
        if st.button("⬅ Back to Dashboard", use_container_width=True):
            st.session_state.admin_page = "home"

    with col6:
        st.empty()