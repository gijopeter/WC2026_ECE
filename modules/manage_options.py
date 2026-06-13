import streamlit as st
from .database import get_questions, get_options, add_option, delete_option


def manage_options():

    st.header("🎯 Poll Options & Points")

    questions = get_questions()

    # ------------------ NO QUESTIONS CASE ------------------
    if questions.empty:
        st.info("Add questions first.")

        st.divider()
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()

        return

    # ------------------ Prepare Display ------------------
    questions = questions.copy()

    questions["display"] = (
        "Poll "
        + questions["poll_no"].astype(str)
        + " - "
        + questions["question_text"]
    )

    # ------------------ Optional Search Filter ------------------
    search_text = st.text_input(
        "Search question",
        placeholder="Type group, team, stage, or poll number..."
    )

    filtered_questions = questions.copy()

    if search_text.strip():
        search_lower = search_text.strip().lower()
        filtered_questions = filtered_questions[
            filtered_questions["display"].str.lower().str.contains(search_lower)
        ]

    if filtered_questions.empty:
        st.info("No questions found for the search.")

        st.divider()
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()

        return

    # ------------------ Add Option ------------------
    with st.form("add_option_form"):
        q_id = st.selectbox(
            "Select Question",
            filtered_questions["id"],
            format_func=lambda x: filtered_questions.loc[
                filtered_questions["id"] == x, "display"
            ].values[0]
        )

        option_text = st.text_input("Option Text")
        points = st.number_input(
            "Points if Correct",
            value=0
        )

        points_incorrect = st.number_input(
            "Points if Incorrect",
            value=0,
            help="Use negative values for penalty"
        )

        submitted = st.form_submit_button("Add Option")

        if submitted and option_text.strip():
            add_option(
                q_id,
                option_text.strip(),
                points,
                points_incorrect
            )
            st.success("✅ Option added")
            st.rerun()

    st.divider()

    # ------------------ Delete Option ------------------
    selected_question = st.selectbox(
        "Select Question to Manage Existing Options",
        filtered_questions["id"],
        format_func=lambda x: filtered_questions.loc[
            filtered_questions["id"] == x, "display"
        ].values[0],
        key="delete_option_question"
    )

    options = get_options(selected_question)

    if not options.empty:
        option_to_delete = st.selectbox(
            "Select Option to Delete",
            options["id"],
            format_func=lambda x: options.loc[
                options["id"] == x, "option_text"
            ].values[0]
        )

        if st.button("Delete Option"):
            delete_option(option_to_delete)
            st.warning("Option deleted")
            st.rerun()
    else:
        st.info("No options yet for this question.")

    st.divider()

    # ------------------ Show Existing Options ------------------
    st.subheader("📋 Existing Options")

    existing_options = get_options(selected_question)

    if existing_options.empty:
        st.info("No options added yet.")
    else:
        st.dataframe(
            existing_options[
            ["option_text", "points", "points_incorrect"]
            ],
            use_container_width=True
        )

    st.divider()

    # ------------------ Back Button ------------------
    if st.button("⬅ Back"):
        st.session_state.admin_page = "polls"
        st.rerun()