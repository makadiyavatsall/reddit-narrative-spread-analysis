# Narrative-Level Analysis of Reddit Content

This project analyzes how **narratives (contexts)** emerge and spread across
Reddit communities over time.

Instead of focusing on individual posts or URLs, the analysis operates at the
**narrative level**—grouping posts by what they are about (e.g. politics,
technology, geopolitics)—to better understand patterns of attention,
amplification, and community involvement on social media.

The project was developed as part of a **Research Engineering Intern assignment**
and is structured as a mini research-to-product pipeline.

---

## 🧩 Problem Motivation

Social media platforms are often analyzed at the level of individual posts or
accounts. However, for research into misinformation, influence, and public
discourse, this granularity is often insufficient.

Researchers are more interested in:
- how **topics and narratives** gain attention,
- how quickly they spread,
- and which communities amplify them.

This project addresses that gap by focusing on **narrative-level dynamics**
instead of post-level popularity.

---

## 📊 Dataset Overview

The dataset consists of Reddit post data provided in JSONL format.

Each record contains post-level information such as:
- post title and text
- subreddit (community)
- author
- timestamp of creation
- optional external URLs

### Important Notes
- The dataset does **not** provide direct engagement metrics such as impressions,
  reach, or explicit share counts.
- Reddit does not expose a native “share” metric; therefore, this project treats
  **each post as an act of narrative amplification**, which is a standard and
  defensible approach in social media research.

---

## 🧠 Research Approach

### 1. Narrative Identification (Explainable NLP)
Posts are grouped into narratives using **keyword-based matching** applied to
post titles and text.

This approach was chosen deliberately because it is:
- transparent
- interpretable
- easy to audit
- suitable for investigative and journalistic contexts

No black-box or opaque models are used.

---

### 2. Amplification as a Proxy for Spread
Since direct share metrics are unavailable, the analysis defines:

> **Amplification = number of posts discussing a narrative**

This allows us to study:
- how often narratives appear,
- how long they persist,
- and how broadly they spread across communities.

---

### 3. Time-Normalized Analysis
Rather than relying on calendar dates alone, narrative growth is analyzed using:

> **Days since first appearance**

This enables fair comparison between narratives that emerged at different times.

---

### 4. Community-Level Analysis
Subreddit-level aggregation is used to understand:
- which communities amplify which narratives,
- whether narratives remain siloed or spread broadly.

---

## 🖥️ System Design

The project is structured into two main components:

### 1. Exploratory Notebook (`SimPpl.ipynb`)
- Initial data exploration
- Narrative keyword design
- Validation of assumptions
- Early trend inspection

This notebook documents the **thinking and research process**.

### 2. Interactive Dashboard (`app.py`)
A Streamlit-based dashboard that allows users to:
- select a global time window (Power BI–style slicing),
- view narrative distribution within that window,
- drill down into individual narratives,
- observe growth dynamics and community amplification,
- read automatically generated, data-driven conclusions.

The dashboard is designed for **investigative analysis**, not just visualization.

---

## 📈 Key Insights

Some general observations from the analysis include:

- Narrative attention on Reddit is **unevenly distributed**, with a small number
  of narratives receiving sustained amplification.
- Different narratives exhibit **distinct growth patterns**, with some peaking
  rapidly while others grow gradually.
- Amplification is often driven by **multiple communities**, rather than a single
  dominant subreddit.
- Narrative spread appears to rely more on **repeated posting across communities**
  than on isolated high-impact posts.

All conclusions are descriptive and intentionally cautious.

---

## ⚠️ Limitations

This project is subject to several limitations:

- No direct measurement of reach or impressions
- No user-level network or follower data
- Analysis limited to Reddit only
- Narrative detection based on keywords rather than semantic embeddings

These constraints are acknowledged and reflected in the interpretation.

---

## ▶️ Running the Project Locally

### Requirements
```bash
pip install -r requirements.txt
