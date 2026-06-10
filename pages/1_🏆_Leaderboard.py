import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from modules.database import (
    init_db,
    calculate_leaderboard,
    calculate_poll_scores,
    calculate_cumulative_trend
)

init_db()

st.title("🏆 World Cup Predictions Leaderboard - Global ECE")

tab1, tab2, tab3 = st.tabs([
    "🏆 Overall Leaderboard",
    "📋 Poll-wise Scores",
    "📈 Trend"
])

with tab1:
    df = calculate_leaderboard()

    if df.empty:
        st.info("No results yet.")
    else:
        if "total_points" in df.columns:
            points_col = "total_points"
        elif "score" in df.columns:
            points_col = "score"
        elif "points" in df.columns:
            points_col = "points"
        else:
            st.error(f"No points column found. Available columns: {list(df.columns)}")
            st.stop()

        df_sorted = df.sort_values(points_col, ascending=False).reset_index(drop=True)
        df_sorted.index = df_sorted.index + 1
        df_sorted.index.name = "Rank"

        df_display = df_sorted.rename(columns={
            "name": "Player",
            "player": "Player",
            "total_points": "Points",
            "score": "Points",
            "points": "Points"
        })

        st.dataframe(df_display, use_container_width=True)

with tab2:
    poll_scores = calculate_poll_scores()

    if poll_scores.empty:
        st.info("No poll-wise scores yet.")
    else:
        poll_options = poll_scores["poll_no"].drop_duplicates().sort_values().tolist()

        selected_poll = st.selectbox(
            "Select Poll",
            poll_options,
            format_func=lambda x: f"Poll {x}"
        )

        poll_df = poll_scores[poll_scores["poll_no"] == selected_poll].copy()

        question_text = poll_df["question_text"].iloc[0]
        st.subheader(f"Poll {selected_poll}: {question_text}")

        poll_df = poll_df.sort_values("score", ascending=False)

        st.dataframe(
            poll_df[["player", "selected_option", "score"]].rename(columns={
                "player": "Player",
                "selected_option": "Selected Option",
                "score": "Points"
            }),
            use_container_width=True,
            hide_index=True
        )

with tab3:
    trend_df = calculate_cumulative_trend(last_n_polls=5, top_n_players=7)

    if trend_df.empty:
        st.info("No trend data yet.")
    else:
        chart_df = trend_df.pivot(
            index="poll_no",
            columns="player",
            values="cumulative_score"
        ).fillna(method="ffill").fillna(0)

        st.subheader("Top 7 Players - Trend Over Last 5 Polls")
        st.line_chart(chart_df)