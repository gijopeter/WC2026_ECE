import os
import tempfile
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .database import (
    calculate_leaderboard,
    calculate_poll_scores
)


def generate_pdf_reports():

    st.header("📄 Generate PDF Reports")

    granularity = st.selectbox(
        "Report Detail Level",
        [
            "Summary only",
            "Summary + Poll scores",
            "Full detail"
        ]
    )

    if st.button("Generate PDF"):

        pdf_path = create_pdf_report(granularity)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=f,
                file_name="worldcup_prediction_report.pdf",
                mime="application/pdf"
            )

    st.divider()

    if st.button("⬅ Back"):
        st.session_state.admin_page = "home"
        st.rerun()


def create_pdf_report(granularity):

    tmp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(tmp_dir, "worldcup_prediction_report.pdf")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("World Cup Prediction Report", styles["Title"]))
    elements.append(Spacer(1, 16))

    leaderboard = calculate_leaderboard()

    elements.append(Paragraph("Overall Leaderboard", styles["Heading2"]))

    if leaderboard.empty:
        elements.append(Paragraph("No leaderboard data available.", styles["Normal"]))
    else:
        points_col = _detect_points_column(leaderboard)

        leaderboard = leaderboard.sort_values(points_col, ascending=False).reset_index(drop=True)

        data = [["Rank", "Player", "Points"]]

        for idx, row in leaderboard.iterrows():
            player = row.get("player", row.get("name", ""))
            points = row[points_col]
            data.append([idx + 1, player, points])

        elements.append(_make_table(data))

    if granularity in ["Summary + Poll scores", "Full detail"]:

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Poll-wise Scores", styles["Heading2"]))

        poll_scores = calculate_poll_scores()

        if poll_scores.empty:
            elements.append(Paragraph("No poll scores available.", styles["Normal"]))
        else:
            for poll_no in sorted(poll_scores["poll_no"].dropna().unique()):

                poll_df = poll_scores[poll_scores["poll_no"] == poll_no]

                question = poll_df["question_text"].iloc[0]

                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Poll {poll_no}: {question}", styles["Heading3"]))

                if granularity == "Summary + Poll scores":
                    data = [["Player", "Score"]]

                    for _, row in poll_df.iterrows():
                        data.append([
                            row["player"],
                            row["score"]
                        ])

                else:
                    data = [["Player", "Selected Option", "Score"]]

                    for _, row in poll_df.iterrows():
                        data.append([
                            row["player"],
                            row["selected_option"],
                            row["score"]
                        ])

                elements.append(_make_table(data))

    doc.build(elements)

    return pdf_path


def _detect_points_column(df):
    for col in ["total_points", "score", "points"]:
        if col in df.columns:
            return col

    raise ValueError(f"No points column found. Available columns: {list(df.columns)}")


def _make_table(data):

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
    ]))

    return table