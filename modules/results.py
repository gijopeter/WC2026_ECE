import streamlit as st
from .database import (
    get_questions,
    get_options,
    get_results,
    save_results_for_question
)


def manage_results():

    st.header("🏆 Enter Poll Results")

    questions = get_questions()

    if questions.empty:
        st.info("Add questions first.")

        st.divider()
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    questions = questions.copy()
    questions["display"] = (
        "Poll " + questions["poll_no"].astype(str) + " - " + questions["question_text"]
    )

    search_text = st.text_input(
        "Search poll",
        placeholder="Type poll number, group, team, stage, or question..."
    )

    filtered_questions = questions.copy()

    if search_text.strip():
        search_lower = search_text.strip().lower()
        filtered_questions = filtered_questions[
            filtered_questions["display"].str.lower().str.contains(search_lower)
        ]

    if filtered_questions.empty:
        st.info("No polls found.")

        st.divider()
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

        st.divider()
        if st.button("⬅ Back"):
            st.session_state.admin_page = "polls"
            st.rerun()
        return

    results = get_results()

    existing_ids = []
    if not results.empty:
        existing_ids = results.loc[
            results["question_id"] == q_id,
            "correct_option_id"
        ].tolist()

    option_id_to_text = dict(zip(options["id"], options["option_text"]))

    if existing_ids:
        existing_texts = [
            option_id_to_text.get(option_id, str(option_id))
            for option_id in existing_ids
        ]
        st.info("Existing saved result(s): ✅ " + ", ".join(existing_texts))

    correct_options = st.multiselect(
        "Correct Option(s)",
        options["id"],
        default=[oid for oid in existing_ids if oid in options["id"].tolist()],
        format_func=lambda x: option_id_to_text[x]
    )

    confirm_update = st.checkbox(
        "I confirm these are the final result option(s)"
    )

    if st.button("Save / Update Result"):

        if not correct_options:
            st.error("Please select at least one correct option.")

        elif not confirm_update:
            st.error("Please confirm before saving the result.")

        else:
            save_results_for_question(q_id, correct_options)
            st.success("✅ Result saved or updated")
            st.rerun()

    st.divider()

    if st.button("⬅ Back"):
        st.session_state.admin_page = "polls"
        st.rerun()