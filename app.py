import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==================================================
# Page Config
# ==================================================
st.set_page_config(
    page_title="Reddit Narrative Spread Analysis",
    layout="centered"
)

# ==================================================
# Title & Context
# ==================================================
st.title("How Narratives Spread Across Reddit")

st.write("""
This dashboard analyzes how **narratives (contexts)** emerge and are amplified
across Reddit communities over time.

A narrative represents a broader topic (e.g. technology, politics, conflict),
identified using transparent keyword-based rules.  
Each post is treated as an **act of amplification**.
""")

# ==================================================
# Load Data
# ==================================================
@st.cache_data
def load_data():
    df = pd.read_json("data.jsonl", lines=True)
    return pd.json_normalize(df["data"])

data_df = load_data()

clean_df = data_df[
    ["subreddit", "author", "created_utc", "title", "selftext"]
].copy()

# ==================================================
# Narrative Definitions (Explainable NLP)
# ==================================================
NARRATIVES = {
    "Technology / Big Tech": [
        "technology", "tech", "ai", "artificial intelligence",
        "google", "meta", "facebook", "twitter", "musk", "data"
    ],
    "Politics / Government": [
        "election", "vote", "government", "policy", "bill",
        "parliament", "congress", "minister", "president", "party"
    ],
    "Geopolitics / Conflict": [
        "war", "attack", "terror", "terrorist", "military",
        "missile", "killed", "invasion", "border", "conflict"
    ],
    "Economy / Jobs": [
        "economy", "inflation", "jobs", "unemployment",
        "recession", "market", "wages", "growth"
    ],
}

# ==================================================
# Text Preparation & Narrative Detection
# ==================================================
clean_df["text"] = (
    clean_df["title"].fillna("") + " " +
    clean_df["selftext"].fillna("")
).str.lower()

def detect_narratives(text):
    matched = []
    for narrative, keywords in NARRATIVES.items():
        for kw in keywords:
            if kw in text:
                matched.append(narrative)
                break
    return matched

clean_df["narratives"] = clean_df["text"].apply(detect_narratives)

narrative_df = clean_df.explode("narratives")
narrative_df = narrative_df.dropna(subset=["narratives"])

# ==================================================
# Time Processing
# ==================================================
narrative_df["created_time"] = pd.to_datetime(
    narrative_df["created_utc"], unit="s"
)

first_seen = (
    narrative_df
    .groupby("narratives")["created_time"]
    .min()
    .reset_index()
    .rename(columns={"created_time": "first_seen"})
)

narrative_df = narrative_df.merge(first_seen, on="narratives", how="left")

narrative_df["days_since_start"] = (
    narrative_df["created_time"] - narrative_df["first_seen"]
).dt.days

# ==================================================
# GLOBAL TIME WINDOW (Power BI–style slicer)
# ==================================================
st.subheader("Global Time Window")

min_day = int(narrative_df["days_since_start"].min())
max_day = int(narrative_df["days_since_start"].max())

day_range = st.slider(
    "Select analysis window (days since narrative first appeared):",
    min_day, max_day, (min_day, max_day)
)

window_df = narrative_df[
    (narrative_df["days_since_start"] >= day_range[0]) &
    (narrative_df["days_since_start"] <= day_range[1])
]

# ==================================================
# GLOBAL KPIs (Time-window aware)
# ==================================================
st.subheader("Dataset Activity (Selected Window)")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total Amplifications", len(window_df))

with c2:
    st.metric("Active Communities", window_df["subreddit"].nunique())

with c3:
    st.metric("Narratives Active", window_df["narratives"].nunique())

# ==================================================
# Narrative Distribution (Selected Window)
# ==================================================
st.subheader("Narrative Distribution in Selected Window")

narrative_counts = (
    window_df["narratives"]
    .value_counts()
    .reset_index()
)

narrative_counts.columns = ["Narrative", "Post Count"]

st.dataframe(narrative_counts, use_container_width=True)

# ==================================================
# Narrative Growth Over Time
# ==================================================
st.subheader("Narrative Growth Dynamics")

narrative_time_df = (
    narrative_df
    .groupby(["days_since_start", "narratives"])
    .size()
    .reset_index(name="count")
)

selected_narrative = st.selectbox(
    "Select a narrative:",
    sorted(narrative_time_df["narratives"].unique())
)

# ==================================================
# Narrative-Specific KPIs (Dynamic)
# ==================================================
selected_df = window_df[
    window_df["narratives"] == selected_narrative
]

peak_row = (
    narrative_time_df[
        narrative_time_df["narratives"] == selected_narrative
    ]
    .sort_values("count", ascending=False)
    .iloc[0]
)

k1, k2, k3 = st.columns(3)

with k1:
    st.metric("Total Amplifications", len(selected_df))

with k2:
    st.metric("Communities Reached", selected_df["subreddit"].nunique())

with k3:
    st.metric("Days to Peak Activity", int(peak_row["days_since_start"]))

# ==================================================
# Timeline Plot (Days Since First Appearance)
# ==================================================
filtered = narrative_time_df[
    narrative_time_df["narratives"] == selected_narrative
]

fig, ax = plt.subplots()
ax.plot(filtered["days_since_start"], filtered["count"], marker="o")
ax.set_xlabel("Days Since Narrative First Appeared")
ax.set_ylabel("Number of Posts")
ax.set_title(f"Growth Pattern: {selected_narrative}")
st.pyplot(fig)

# ==================================================
# Community Amplification
# ==================================================
st.subheader("Community Amplification (Selected Window)")

community_counts = (
    selected_df
    .groupby("subreddit")
    .size()
    .sort_values(ascending=False)
    .head(10)
)

fig2, ax2 = plt.subplots()
community_counts.plot(kind="bar", ax=ax2)
ax2.set_xlabel("Subreddit")
ax2.set_ylabel("Number of Posts")
ax2.set_title("Top Communities Amplifying This Narrative")
st.pyplot(fig2)

# ==================================================
# Key Observations & Conclusions
# ==================================================
st.subheader("Key Observations from the Analysis")

if len(window_df) == 0:
    st.write(
        "No posts fall within the selected time window. "
        "Please expand the window to view narrative activity."
    )
else:
    # Dominant narrative in selected window
    dominant_narrative = (
        window_df["narratives"]
        .value_counts()
        .idxmax()
    )

    # Average activity per day
    avg_posts_per_day = (
        window_df
        .groupby("days_since_start")
        .size()
        .mean()
    )

    # Narrative-specific slice (recomputed safely)
    selected_df_local = window_df[
        window_df["narratives"] == selected_narrative
    ]

    # Communities reached (local computation)
    communities_reached_local = selected_df_local["subreddit"].nunique()

    # Days to peak activity (local computation)
    peak_row_local = (
        narrative_time_df[
            narrative_time_df["narratives"] == selected_narrative
        ]
        .sort_values("count", ascending=False)
        .iloc[0]
    )

    days_to_peak_local = int(peak_row_local["days_since_start"])

    st.write(
        f"""
        **1. Dominant Narrative**  
        During the selected time window, discussions were most concentrated around
        the **{dominant_narrative}** narrative. This suggests that this topic received
        comparatively higher attention from Reddit users in this period.

        **2. Speed of Attention Growth**  
        The selected narrative reached its peak activity approximately
        **{days_to_peak_local} days** after first appearing. This indicates how quickly
        attention formed around the topic once it entered discussion.

        **3. Community Involvement**  
        The narrative was discussed across **{communities_reached_local} different subreddits**,
        suggesting that attention was not limited to a single community but spread
        across multiple audiences.

        **4. Overall Activity Level**  
        On average, Reddit saw approximately **{avg_posts_per_day:.1f} narrative-related posts per day**
        within the selected window. This reflects a moderate but sustained level of engagement.

        **Overall Interpretation**  
        Taken together, these patterns suggest that narrative spread on Reddit is driven
        by repeated amplification across communities rather than by isolated high-impact posts.
        """
    )
