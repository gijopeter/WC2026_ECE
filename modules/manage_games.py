import streamlit as st
from .database import get_games, add_game, delete_game, get_teams


def manage_games():

    st.header("🏟 Manage Games")

    games = get_games()
    teams = get_teams()

    STAGE_OPTIONS = [
        "Group Stage",
        "Round of 32",
        "Round of 16",
        "Quarter final",
        "Semi final",
        "Loser's final",
        "Final"
    ]

    GROUP_OPTIONS = [
        "",
        "Group A",
        "Group B",
        "Group C",
        "Group D",
        "Group E",
        "Group F",
        "Group G",
        "Group H",
        "Group I",
        "Group J",
        "Group K",
        "Group L",
    ]

    # ------------------ Add Game ------------------
    st.subheader("➕ Add Game")

    with st.form("add_game_form"):

        if not teams.empty:
            team1 = st.selectbox("Select Team 1", teams["name"])
            team2 = st.selectbox("Select Team 2", teams["name"], index=1)
        else:
            st.info("Add teams first in the database.")
            team1 = None
            team2 = None

        stage = st.selectbox("Stage", STAGE_OPTIONS)

        group_name = st.selectbox(
            "Group",
            GROUP_OPTIONS,
            help="Use this mainly for group-stage games. Leave empty for knockout games."
        )

        submitted = st.form_submit_button("Add Game")

        if submitted and team1 and team2:

            if team1 == team2:
                st.error("Cannot select the same team for both sides!")

            else:
                sorted_new = sorted([team1, team2])
                game_name_new = f"{sorted_new[0]} vs {sorted_new[1]}"

                if "group_name" not in games.columns:
                    games["group_name"] = ""

                existing_normalized = games["name"].apply(
                    lambda x: " vs ".join(sorted([t.strip() for t in x.split(" vs ")]))
                )

                duplicate = games[
                    (existing_normalized == game_name_new)
                    & (games["stage"] == stage)
                    & (games["group_name"].fillna("") == group_name)
                ]

                if not duplicate.empty:
                    st.error(f"Game '{game_name_new}' ({stage}, {group_name}) already exists!")
                else:
                    add_game(game_name_new, stage, group_name if group_name else None)
                    st.success(f"✅ '{game_name_new}' added")
                    st.rerun()

    st.divider()

    # ------------------ Filter Games ------------------
    if not games.empty:

        st.subheader("🔎 Filter Games")

        if "group_name" not in games.columns:
            games["group_name"] = ""

        group_values = sorted(games["group_name"].dropna().unique().tolist())
        group_filter = st.selectbox("Filter by Group", ["All"] + group_values)

        stage_values = sorted(games["stage"].dropna().unique().tolist())
        stage_filter = st.selectbox("Filter by Stage", ["All"] + stage_values)

        filtered_games = games.copy()

        if group_filter != "All":
            filtered_games = filtered_games[filtered_games["group_name"] == group_filter]

        if stage_filter != "All":
            filtered_games = filtered_games[filtered_games["stage"] == stage_filter]

        st.divider()

        # ------------------ Display + Delete Games ------------------
        st.subheader("🗑 Delete Games")

        if filtered_games.empty:
            st.info("No games found for the selected filter.")

        else:
            filtered_games["display"] = (
                filtered_games["group_name"].fillna("") + " - " +
                filtered_games["name"] + " (" +
                filtered_games["stage"] + ")"
            )

            selected_to_delete = []

            for _, row in filtered_games.iterrows():
                if st.checkbox(row["display"], key=f"del_{row['id']}"):
                    selected_to_delete.append(row["id"])

            if st.button("Delete Selected Games"):
                if selected_to_delete:
                    for game_id in selected_to_delete:
                        delete_game(game_id)

                    st.success("✅ Selected games deleted")
                    st.rerun()
                else:
                    st.warning("Select at least one game to delete")

    else:
        st.info("No games added yet.")

    st.divider()

    if st.button("⬅ Back"):
        st.session_state.admin_page = "home"
        st.rerun()