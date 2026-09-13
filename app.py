"""
NBA Player Profiles -- Streamlit dashboard

A simple, beginner-friendly dashboard version of the analysis in
notebooks/nba_player_analysis.ipynb. It reads the already-cleaned,
feature-engineered CSV (no recalculation of raw data here) and displays
the same insights, player profile, and player comparison logic through
an interactive UI instead of notebook cells.

Run with: streamlit run app.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="NBA Player Profiles", page_icon="🏀", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("data/nba_player_stats_2024_25_features.csv")


df = load_data()

st.title("🏀 NBA Player Profiles: 2024-25 Season")
st.caption(
    "A beginner data science portfolio project -- pandas, simple math, and "
    "transparent rules only. No machine learning."
)

tab_overview, tab_profile, tab_compare, tab_insights = st.tabs(
    ["Overview", "Player Profile", "Compare Players", "Insights"]
)

# ---------------------------------------------------------------------------
# Overview tab
# ---------------------------------------------------------------------------
with tab_overview:
    st.subheader("Dataset at a glance")
    col1, col2, col3 = st.columns(3)
    col1.metric("Players (after filtering)", len(df))
    col2.metric("Average PPG", f"{df['PPG'].mean():.1f}")
    col3.metric("Average All-Around Score", f"{df['ALL_AROUND_SCORE'].mean():.1f}")

    st.caption(
        "\"Filtering\" means players with fewer than 20 games or 10 minutes "
        "per game were removed -- see the notebook's Step 2 for why."
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Top 10 Scorers**")
        top_scorers = df.sort_values("PPG", ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.barh(top_scorers["PLAYER"], top_scorers["PPG"], color="#1f77b4")
        ax.invert_yaxis()
        ax.set_xlabel("Points Per Game")
        st.pyplot(fig)

    with chart_col2:
        st.markdown("**Top 10 by All-Around Score (experimental)**")
        top_all_around = df.sort_values("ALL_AROUND_SCORE", ascending=False).head(10)
        fig, ax = plt.subplots()
        ax.barh(top_all_around["PLAYER"], top_all_around["ALL_AROUND_SCORE"], color="#17becf")
        ax.invert_yaxis()
        ax.set_xlabel("All-Around Score (0-100)")
        st.pyplot(fig)

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("**Player Archetype Distribution**")
        counts = df["ARCHETYPE"].value_counts()
        fig, ax = plt.subplots()
        ax.barh(counts.index, counts.values, color="#8c564b")
        ax.invert_yaxis()
        ax.set_xlabel("Number of Players")
        st.pyplot(fig)

    with chart_col4:
        st.markdown("**Correlation Between Major Stats**")
        stat_cols = ["MIN", "PPG", "APG", "RPG", "SPG", "BPG", "TOV", "FG_PCT", "FG3_PCT", "FT_PCT"]
        corr = df[stat_cols].corr()
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(stat_cols)))
        ax.set_xticklabels(stat_cols, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(stat_cols)))
        ax.set_yticklabels(stat_cols, fontsize=7)
        for i in range(len(stat_cols)):
            for j in range(len(stat_cols)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6)
        fig.colorbar(im, ax=ax, label="Correlation", shrink=0.8)
        st.pyplot(fig)

# ---------------------------------------------------------------------------
# Player Profile tab
# ---------------------------------------------------------------------------
with tab_profile:
    st.subheader("Look up a player")
    player_name = st.selectbox("Choose a player", sorted(df["PLAYER"].unique()))
    player = df[df["PLAYER"] == player_name].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Team", player["TEAM"])
    col2.metric("Position", player["POSITION"])
    col3.metric("Archetype", player["ARCHETYPE"])

    st.markdown("**Per game**")
    cols = st.columns(5)
    for col, stat in zip(cols, ["PPG", "APG", "RPG", "SPG", "BPG"]):
        col.metric(stat, f"{player[stat]:.1f}")

    st.markdown("**Shooting**")
    cols = st.columns(3)
    for col, stat, label in zip(cols, ["FG_PCT", "FG3_PCT", "FT_PCT"], ["FG%", "3P%", "FT%"]):
        col.metric(label, f"{player[stat]:.1%}")

    st.markdown("**Per 36 minutes**")
    cols = st.columns(3)
    for col, stat, label in zip(cols, ["PTS_per_36", "AST_per_36", "REB_per_36"], ["PTS", "AST", "REB"]):
        col.metric(label, f"{player[stat]:.1f}")

    st.metric("All-Around Score (experimental, 0-100)", player["ALL_AROUND_SCORE"])

    st.markdown(f"**{player_name} vs. League Average**")
    stats = ["PPG", "APG", "RPG", "SPG", "BPG"]
    player_values = [player[s] for s in stats]
    league_avg = [df[s].mean() for s in stats]

    x = range(len(stats))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar([i - width / 2 for i in x], player_values, width, label=player_name)
    ax.bar([i + width / 2 for i in x], league_avg, width, label="League Average")
    ax.set_xticks(list(x))
    ax.set_xticklabels(stats)
    ax.set_ylabel("Per Game")
    ax.legend()
    st.pyplot(fig)

# ---------------------------------------------------------------------------
# Compare Players tab
# ---------------------------------------------------------------------------
with tab_compare:
    st.subheader("Compare two players")
    all_players = sorted(df["PLAYER"].unique())
    col1, col2 = st.columns(2)
    player_a_name = col1.selectbox("Player A", all_players, index=0, key="player_a")
    player_b_name = col2.selectbox("Player B", all_players, index=1, key="player_b")

    player_a = df[df["PLAYER"] == player_a_name].iloc[0]
    player_b = df[df["PLAYER"] == player_b_name].iloc[0]

    compare_cols = [
        "TEAM", "POSITION", "ARCHETYPE",
        "PPG", "APG", "RPG", "SPG", "BPG",
        "FG_PCT", "FG3_PCT", "FT_PCT",
        "PTS_per_36", "AST_per_36", "REB_per_36",
        "ALL_AROUND_SCORE",
    ]
    percent_cols = {"FG_PCT", "FG3_PCT", "FT_PCT"}
    decimal_cols = {"PPG", "APG", "RPG", "SPG", "BPG", "PTS_per_36", "AST_per_36", "REB_per_36", "ALL_AROUND_SCORE"}

    def format_stat(col, value):
        # Format each stat for display -- and convert everything to a string
        # so the comparison table has one consistent type per column
        # (a mix of text and numbers in the same column trips up Streamlit's
        # table renderer).
        if col in percent_cols:
            return f"{value:.1%}"
        if col in decimal_cols:
            return f"{value:.1f}"
        return str(value)

    comparison = pd.DataFrame(
        {
            player_a_name: [format_stat(c, player_a[c]) for c in compare_cols],
            player_b_name: [format_stat(c, player_b[c]) for c in compare_cols],
        },
        index=compare_cols,
    )
    st.dataframe(comparison, width="stretch")

    stats = ["PPG", "APG", "RPG", "SPG", "BPG"]
    x = range(len(stats))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar([i - width / 2 for i in x], player_a[stats], width, label=player_a_name)
    ax.bar([i + width / 2 for i in x], player_b[stats], width, label=player_b_name)
    ax.set_xticks(list(x))
    ax.set_xticklabels(stats)
    ax.set_ylabel("Per Game")
    ax.legend()
    st.pyplot(fig)

# ---------------------------------------------------------------------------
# Insights tab
# ---------------------------------------------------------------------------
with tab_insights:
    st.markdown("""
Each insight below follows **Observation -> Evidence -> Interpretation**, and traces back to a
specific number produced by this same dataset (see the notebook for the full derivation).

**1. Playing time is the single strongest driver of raw production.**
Minutes correlate 0.87 with points per game -- a major reason per-36 stats matter for fair
comparison between bench players and starters.

**2. Ball-handling responsibility comes bundled with turnover risk.**
Assists and turnovers are the most correlated pair in the dataset (0.85) -- raw turnover counts
alone are a poor measure of ball security.

**3. Scoring, playmaking, and rebounding leaderboards are mostly separate groups of players.**
The Top 10 lists for points, assists, and rebounds share almost no players -- only Nikola Jokić
appears in all three.

**4. Interior defense and rebounding form their own skill cluster.**
`RPG` and `BPG` correlate at 0.65, while `BPG`-`APG` is essentially 0 -- rebounding/shot-blocking
behaves as a distinct statistical dimension from passing.

**5. Field goal percentage systematically favors centers over 3-point shooters.**
`FG_PCT` and `FG3_PCT` are negatively correlated (-0.48) -- a simple "efficiency" ranking by FG%
quietly favors one style of play over another.

**6. The All-Around Score surfaces different "best players" than pure scoring totals.**
Nikola Jokić leads the All-Around Score despite ranking 3rd in scoring; Victor Wembanyama ranks
2nd overall without leading any single category outright.

**7. Most rotation players are statistically "Role Players" -- true two-way threats are rare.**
198 of 411 players (48%) were classified `Role Player`, versus only 4 (1%) as `Two-Way Player`.

**8. Two players can reach similar overall value through very different statistical paths.**
Shai Gilgeous-Alexander and Luka Dončić post nearly identical All-Around Scores (53.2 vs. 55.0)
via different stat mixes -- try comparing them yourself in the "Compare Players" tab.
""")
