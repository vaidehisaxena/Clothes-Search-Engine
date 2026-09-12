import os
from pathlib import Path

import streamlit as st

from search_engine import ClothingSearchEngine


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "corpus_100.txt"
OUTPUT_DIR = ROOT / "outputs"


@st.cache_resource
def load_engine():
    engine = ClothingSearchEngine()
    if DATA_PATH.exists():
        engine.build_index(str(DATA_PATH))
        engine.save_indexes(
            os.path.join(str(OUTPUT_DIR), "dictionary.json"),
            os.path.join(str(OUTPUT_DIR), "positional_index.json"),
        )
    return engine


st.set_page_config(page_title="Clothing Search Engine", page_icon="🧥", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #111827 0%, #0f172a 35%, #020617 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [role="tablist"] {
        gap: 0.6rem;
    }
    .stTabs [role="tab"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px 12px 0 0;
        color: #cbd5e1;
        padding: 0.65rem 1rem;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b, #f97316);
        color: #111827;
        font-weight: 700;
    }
    div[data-testid="stSelectbox"], div[data-testid="stTextInput"], div[data-testid="stNumberInput"] {
        background: rgba(15, 23, 42, 0.75);
        border-radius: 12px;
        color: #e5e7eb;
    }
    .stButton > button {
        border-radius: 12px;
        border: none;
        font-weight: 700;
        background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        color: #111827;
        padding: 0.8rem 1.2rem;
        box-shadow: 0 10px 25px rgba(249, 115, 22, 0.35);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(249, 115, 22, 0.4);
    }
    .result-card {
        background: linear-gradient(180deg, rgba(15,23,42,0.82), rgba(17,24,39,0.9));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.4);
    }
    .result-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.35;
    }
    .result-meta {
        color: #cbd5e1;
        font-size: 0.92rem;
        margin-top: 0.3rem;
    }
    .score-pill {
        display: inline-block;
        background: rgba(245, 158, 11, 0.18);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.25);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.78rem;
        font-weight: 700;
        margin-top: 0.6rem;
    }
    .stWarning {
        background: rgba(251, 146, 60, 0.12);
        border: 1px solid rgba(251, 146, 60, 0.25);
        color: #fcd34d;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧥 Clothing Search Engine")
st.caption("Luxury-style apparel retrieval for ranked, phrase, and proximity search")

engine = load_engine()

if not DATA_PATH.exists():
    st.error("The corpus file is missing. Please add data/corpus_100.txt.")
    st.stop()

mode = st.selectbox("Search mode", ["Ranked VSM", "Exact phrase", "Ordered proximity"], index=0)

if mode == "Ranked VSM":
    query = st.text_input("Enter a free-text query", value="cotton shirt")
    search_clicked = st.button("Search catalog", use_container_width=True)

    if search_clicked:
        results = engine.ranked_search(query, limit=10)
        if not results:
            st.warning("No matching documents were found.")
        else:
            for result in results:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-title">{result['docID']} — {result['title']}</div>
                        <div class="result-meta">Category: {result['category']}</div>
                        <span class="score-pill">Score: {result['score']:.6f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

elif mode == "Exact phrase":
    phrase = st.text_input("Enter an exact phrase", value="stretch denim")
    search_clicked = st.button("Find phrase", use_container_width=True)

    if search_clicked:
        results = engine.phrase_search(phrase)
        if not results:
            st.warning("No exact phrase matches were found.")
        else:
            for result in results:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-title">{result['docID']} — {result['title']}</div>
                        <div class="result-meta">Category: {result['category']}</div>
                        <div class="result-meta">Matched positions: {result['matched_positions']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

else:
    col1, col2 = st.columns(2)
    with col1:
        first_term = st.text_input("First term", value="cotton")
    with col2:
        second_term = st.text_input("Second term", value="shirt")

    k = st.number_input("Maximum ordered distance (k)", min_value=1, value=3)
    search_clicked = st.button("Check proximity", use_container_width=True)

    if search_clicked:
        results = engine.proximity_search(first_term, second_term, int(k))
        if not results:
            st.warning("No proximity matches were found.")
        else:
            for result in results:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-title">{result['docID']} — {result['title']}</div>
                        <div class="result-meta">Category: {result['category']}</div>
                        <div class="result-meta">Pairs: {result['matches']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
