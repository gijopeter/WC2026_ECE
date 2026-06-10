import os
import pandas as pd
import streamlit as st

SNAPSHOT_FILE = "data/leaderboard_snapshot.xlsx"

st.title("🏆 World Cup Predictions Leaderboard - Global ECE")

if not os.path.exists(SNAPSHOT_FILE):
    st.info("Leaderboard snapshot not available yet.")
    st.stop()

leaderboard = pd.read_excel(SNAPSHOT_FILE, sheet_name="Leaderboard")
poll_scores = pd.read_excel(SNAPSHOT_FILE, sheet_name="PollScores")

try:
    trend_df = pd.read_excel(SNAPSHOT_FILE, sheet_name="Trend")
except Exception:
    trend_df = pd.DataFrame()

tab1, tab2, tab3 = st.tabs([
    "🏆 Overall Leaderboard",
    "📋 Poll-wise Scores",
    "📈 Trend"
])

with tab1:
    if leaderboard.empty:
        st.info("No results yet.")
    else:
        if "total_points" in leaderboard.columns:
            points_col = "total_points"
        elif "score" in leaderboard.columns:
            points_col = "score"
        elif "points" in leaderboard.columns:
            points_col = "points"
        else:
            st.error(f"No points column found. Available columns: {list(leaderboard.columns)}")
            st.stop()

        df_sorted = leaderboard.sort_values(points_col, ascending=False).reset_index(drop=True)
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
    if trend_df.empty:
        st.info("No trend data yet.")
    else:
        chart_df = trend_df.pivot(
            index="poll_no",
            columns="player",
            values="cumulative_score"
        ).ffill().fillna(0)

        st.subheader("Top 7 Players - Trend Over Last 5 Polls")
        st.line_chart(chart_df)