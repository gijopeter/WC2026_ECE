import streamlit as st
from .database import (
    get_players,
    get_questions,
    get_options,
    save_selection,
    get_saved_selections_for_question,
    delete_selections_for_question,
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
    questions["display"] = (
        "Poll "
        + questions["poll_no"].astype(str)
        + " - "
        + questions["question_text"]
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

    options = get_options(q_id)

    if options.empty:
        st.info("No options available for this poll.")
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    st.divider()
    st.subheader("🧑‍🤝‍🧑 Enter Selections by Option")

    player_id_to_name = dict(zip(players["id"], players["name"]))

    selections_by_option = {}

    for _, option in options.iterrows():
        selected_players = st.multiselect(
            f"Players who selected: {option['option_text']}",
            players["id"],
            format_func=lambda x: player_id_to_name[x],
            key=f"option_players_{q_id}_{option['id']}"
        )

        selections_by_option[option["id"]] = selected_players

    st.warning(
        "Saving will replace all previously saved selections for this poll."
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

        if duplicate_players:
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
                save_selection(player_id, q_id, option_id)

        st.success("✅ Existing selections replaced successfully")
        st.rerun()

    st.divider()

    st.subheader("📋 Saved Selections for This Poll")

    saved_selections = get_saved_selections_for_question(q_id)

    if saved_selections.empty:
        st.info("No selections saved yet for this poll.")
    else:
        st.dataframe(
            saved_selections[["player", "selected_option"]],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    if st.button("⬅ Back"):
        st.session_state.admin_page = "polls"
        st.rerun()