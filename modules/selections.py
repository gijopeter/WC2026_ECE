import streamlit as st
from .database import (
    get_players,
    get_questions,
    get_options,
    save_selection,
    get_saved_selections_for_question,
    delete_selections_for_question,
    add_selection_without_delete,
)


def manage_selections():

    st.header("🗳 Enter Player Selections")

    players = get_players()
    questions = get_questions()

    if questions.empty:
        st.info("Add questions first.")
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    if players.empty:
        st.info("Add players first.")
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    questions = questions.copy()

    if "selection_type" not in questions.columns:
        questions["selection_type"] = "single"

    questions["display"] = (
        "Poll "
        + questions["poll_no"].astype(str)
        + " - "
        + questions["question_text"]
        + " ["
        + questions["selection_type"].fillna("single")
        + "]"
    )

    search_text = st.text_input(
        "Search question",
        placeholder="Type poll number, group, team, stage, or question..."
    )

    filtered_questions = questions.copy()

    if search_text.strip():
        search_lower = search_text.strip().lower()
        filtered_questions = filtered_questions[
            filtered_questions["display"].str.lower().str.contains(search_lower)
        ]

    if filtered_questions.empty:
        st.info("No questions found.")
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    q_id = st.selectbox(
        "Select Poll",
        filtered_questions["id"],
        format_func=lambda x: filtered_questions.loc[
            filtered_questions["id"] == x, "display"
        ].values[0]
    )

    selected_question = questions[questions["id"] == q_id].iloc[0]
    selection_type = selected_question.get("selection_type", "single") or "single"

    st.info(f"Selection type: {selection_type}")

    options = get_options(q_id)

    if options.empty:
        st.info("No options available for this poll.")
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    saved_selections = get_saved_selections_for_question(q_id)

    player_id_to_name = dict(zip(players["id"], players["name"]))

    saved_by_option = {}

    if not saved_selections.empty:
        for _, row in saved_selections.iterrows():

            option_text = row["selected_option"]
            player_name = row["player"]

            matching_option = options[
                options["option_text"] == option_text
            ]

            matching_player = players[
                players["name"] == player_name
            ]

            if not matching_option.empty and not matching_player.empty:
                option_id = matching_option.iloc[0]["id"]
                player_id = matching_player.iloc[0]["id"]

                saved_by_option.setdefault(option_id, []).append(player_id)

    st.divider()
    st.subheader("🧑‍🤝‍🧑 Enter Selections by Option")

    selections_by_option = {}

    for _, option in options.iterrows():

        default_players = saved_by_option.get(option["id"], [])

        selected_players = st.multiselect(
            f"{option['option_text']} ({len(default_players)} saved)",
            players["id"],
            default=default_players,
            format_func=lambda x: player_id_to_name[x],
            key=f"option_players_{q_id}_{option['id']}"
        )

        st.caption(f"Currently selected: {len(selected_players)} player(s)")

        selections_by_option[option["id"]] = selected_players

    st.warning(
        "Saving will replace all previously saved selections for this poll."
    )

    if selection_type == "single":
        st.caption(
            "Single-option poll: each player may be selected under only one option."
        )
    else:
        st.caption(
            "Multi-option poll: a player may be selected under multiple options."
        )

    confirm_replace = st.checkbox(
        "I confirm that existing selections for this poll should be replaced"
    )

    if st.button("Save All Selections"):

        if not confirm_replace:
            st.error("Please confirm before replacing existing selections.")
            return

        used_players = []

        for option_id, selected_players in selections_by_option.items():
            for player_id in selected_players:
                used_players.append(player_id)

        duplicate_players = [
            player_id for player_id in used_players
            if used_players.count(player_id) > 1
        ]

        if selection_type == "single" and duplicate_players:
            duplicate_names = sorted(
                {player_id_to_name[player_id] for player_id in duplicate_players}
            )

            st.error(
                "Some players were selected for multiple options: "
                + ", ".join(duplicate_names)
            )
            return

        delete_selections_for_question(q_id)

        for option_id, selected_players in selections_by_option.items():
            for player_id in selected_players:
                if selection_type == "multi":
                    add_selection_without_delete(player_id, q_id, option_id)
                else:
                    save_selection(player_id, q_id, option_id)

        st.success("✅ Existing selections replaced successfully")
        st.rerun()

    st.divider()

    st.subheader("📊 Selection Summary")

    saved_selections = get_saved_selections_for_question(q_id)

    if saved_selections.empty:
        st.info("No selections saved yet for this poll.")
    else:
        summary = (
            saved_selections.groupby("selected_option")
            .size()
            .reset_index(name="players")
            .sort_values("players", ascending=False)
        )

        st.dataframe(
            summary.rename(columns={
                "selected_option": "Option",
                "players": "Players"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("📋 Saved Selections for This Poll")

        st.dataframe(
            saved_selections[["player", "selected_option"]],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    if st.button("⬅ Back"):
        if "admin_authenticated" in st.session_state:
            st.session_state.admin_page = "polls"
            st.rerun()
        else:
            st.info("You are already on the volunteer entry page.")