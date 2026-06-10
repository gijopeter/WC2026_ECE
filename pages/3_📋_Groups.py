import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="World Cup Groups",
    page_icon="📋",
    layout="wide"
)

st.title("📋 World Cup 2026 Group Reference")

GROUPS = {
    "Group A": [
        "Mexico (15)",
        "South Africa (56)",
        "Korea Republic (25)",
        "Czechia (29)"
    ],

    "Group B": [
        "Canada (30)",
        "Switzerland (19)",
        "Qatar (48)",
        "Bosnia and Herzegovina (68)"
    ],

    "Group C": [
        "Brazil (6)",
        "Morocco (8)",
        "Scotland (44)",
        "Haiti (83)"
    ],

    "Group D": [
        "United States (16)",
        "Paraguay (53)",
        "Australia (27)",
        "Türkiye (22)"
    ],

    "Group E": [
        "Germany (10)",
        "Curaçao (82)",
        "Côte d'Ivoire (34)",
        "Ecuador (23)"
    ],

    "Group F": [
        "Netherlands (7)",
        "Japan (18)",
        "Sweden (38)",
        "Tunisia (41)"
    ],

    "Group G": [
        "Belgium (9)",
        "Egypt (29)",
        "IR Iran (21)",
        "New Zealand (94)"
    ],

    "Group H": [
        "Spain (2)",
        "Cape Verde (69)",
        "Saudi Arabia (58)",
        "Uruguay (17)"
    ],

    "Group I": [
        "France (1)",
        "Senegal (14)",
        "Iraq (59)",
        "Norway (31)"
    ],

    "Group J": [
        "Argentina (3)",
        "Algeria (28)",
        "Austria (24)",
        "Jordan (64)"
    ],

    "Group K": [
        "Portugal (5)",
        "Congo DR (61)",
        "Uzbekistan (57)",
        "Colombia (13)"
    ],

    "Group L": [
        "England (4)",
        "Croatia (11)",
        "Ghana (74)",
        "Panama (33)"
    ],
}

cols = st.columns(3)

for idx, (group, teams) in enumerate(GROUPS.items()):

    with cols[idx % 3]:

        st.subheader(group)

        df = pd.DataFrame({
            "Team (FIFA Rank)": teams
        })

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )

st.caption("FIFA rankings approximate based on latest available 2026 rankings.")