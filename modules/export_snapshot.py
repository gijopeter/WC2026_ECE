import streamlit as st
from .database import (
    calculate_leaderboard,
    calculate_poll_scores
)

import pandas as pd
import os


def export_snapshot():

    st.header("📤 Export Leaderboard Snapshot")

    if st.button("Generate Snapshot Excel"):

        output_file = "data/leaderboard_snapshot.xlsx"

        os.makedirs("data", exist_ok=True)

        leaderboard = calculate_leaderboard()
        poll_scores = calculate_poll_scores()

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

            leaderboard.to_excel(
                writer,
                sheet_name="Leaderboard",
                index=False
            )

            poll_scores.to_excel(
                writer,
                sheet_name="PollScores",
                index=False
            )

        st.success(
            f"Snapshot generated successfully:\n{output_file}"
        )

    st.divider()

    if st.button("⬅ Back"):
        st.session_state.admin_page = "home"
        st.rerun()