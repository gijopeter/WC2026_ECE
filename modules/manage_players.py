import streamlit as st
from .database import get_players, add_player, delete_player

def manage_players():
    st.header("👤 Manage Players")
    players = get_players()

    # Add Player
    st.subheader("Add New Player")
    name = st.text_input("Player Name", key="player_name")
    if st.button("Add Player"):
        if name.strip():
            add_player(name.strip())
            st.success("Player added")
            st.rerun()

    st.divider()

    # Delete Player
    if not players.empty:
        st.subheader("Delete Player")
        player_to_delete = st.selectbox(
            "Select Player",
            players["id"],
            format_func=lambda x: players.loc[players["id"] == x, "name"].values[0]
        )
        if st.button("Delete Player"):
            delete_player(player_to_delete)
            st.warning("Player deleted")
            st.rerun()

        st.divider()
        st.dataframe(players, use_container_width=True)
    else:
        st.info("No players yet.")

    if st.button("⬅ Back"):
        st.session_state.admin_page = "home"
        st.rerun()