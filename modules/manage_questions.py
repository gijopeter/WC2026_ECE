import streamlit as st
import pandas as pd
from .database import get_games, get_questions, add_question, delete_question


def manage_questions():
    st.header("❓ Manage Poll Questions")

    st.subheader("➕ Add Poll Question")

    poll_no = st.number_input("Poll Number", min_value=1, step=1)

    question_type = st.radio(
        "Question Type",
        ["Game-specific", "General"],
        horizontal=True
    )

    selected_game_id = None
    selected_game_display = None

    if question_type == "Game-specific":
        games = get_games()

        filtered_games = games.copy()        

        if not games.empty:
            if "group_name" not in games.columns:
                games["group_name"] = ""

            # -------- Stage Filter --------
            stage_values = sorted(
                filtered_games["stage"].dropna().unique().tolist()
            )

            stage_filter = st.selectbox(
                "Filter Games by Stage",
                ["All"] + stage_values
            )

            if stage_filter != "All":
                filtered_games = filtered_games[
                    filtered_games["stage"] == stage_filter
                ]

            # -------- Group Filter --------
            group_values = sorted(
                filtered_games["group_name"].dropna().unique().tolist()
            )

            group_filter = st.selectbox(
                "Filter Games by Group",
                ["All"] + group_values
            )

            if group_filter != "All":
                filtered_games = filtered_games[
                    filtered_games["group_name"] == group_filter
                ]

            # -------- Select Game --------
            if filtered_games.empty:
                st.info("No games found for the selected filters.")

            else:
                filtered_games["display"] = (
                    filtered_games["group_name"].fillna("") + " - " +
                    filtered_games["name"] + " (" +
                    filtered_games["stage"] + ")"
                )

                selected_game_id = st.selectbox(
                    "Select Game",
                    filtered_games["id"],
                    format_func=lambda x: filtered_games.loc[
                        filtered_games["id"] == x, "display"
                    ].values[0]
                )

                selected_game_display = filtered_games.loc[
                    filtered_games["id"] == selected_game_id,
                    "display"
                ].values[0]

        else:
            st.info("Add games first.")

    question_text = st.text_input("Question Text", key="question_text_input")

    if st.button("Add Question"):

        if not question_text.strip():
            st.error("Question text cannot be empty.")

        elif question_type == "Game-specific" and selected_game_id is None:
            st.error("Please select a game.")

        else:
            questions = get_questions()

            if "poll_no" in questions.columns:
                existing_poll_nos = questions["poll_no"].dropna().astype(int).tolist()
            else:
                existing_poll_nos = []

            if int(poll_no) in existing_poll_nos:
                st.error(f"Poll Number {poll_no} already exists. Use a unique number.")

            else:
                if question_type == "Game-specific":
                    final_question_text = (
                        f"{selected_game_display} - {question_text.strip()}"
                    )
                else:
                    final_question_text = question_text.strip()

                add_question(
                    selected_game_id,
                    final_question_text,
                    int(poll_no)
                )

                st.success(f"✅ Poll {poll_no} added successfully")
                st.rerun()

    st.divider()

    questions = get_questions()

    if not questions.empty:
        st.subheader("🗑 Delete Poll Question")

        questions["display"] = (
            questions["question_text"] +
            " [Poll " +
            questions["poll_no"].astype(str) +
            "]"
        )

        selected_questions = []

        for _, row in questions.iterrows():
            if st.checkbox(row["display"], key=f"del_q_{row['id']}"):
                selected_questions.append(row["id"])

        if st.button("Delete Selected Questions"):

            if selected_questions:
                for qid in selected_questions:
                    delete_question(qid)

                st.success("✅ Selected questions deleted")
                st.rerun()

            else:
                st.warning("Select at least one question to delete")

    else:
        st.info("No questions added yet.")

    st.divider()

    if st.button("⬅ Back"):
        st.session_state.admin_page = "polls"
        st.rerun()