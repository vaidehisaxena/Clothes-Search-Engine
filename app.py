"""Polished Streamlit interface for the clothing search engine."""

from html import escape
from pathlib import Path

import streamlit as st

from search_engine import ClothingSearchEngine


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "corpus_100.txt"
OUTPUT_DIR = ROOT / "outputs"

CATEGORY_ICONS = {
    "T-Shirt": "T", "Shirt": "S", "Jeans": "J", "Kurta": "K",
    "Saree": "Sa", "Dress": "D", "Hoodie": "H", "Jacket": "Ja",
    "Leggings": "L", "Sweatshirt": "Sw",
}


@st.cache_resource
def load_engine():
    """Build and cache the index once for the current app process."""
    engine = ClothingSearchEngine()
    engine.build_index(DATA_PATH)
    engine.save_indexes(
        OUTPUT_DIR / "dictionary.json",
        OUTPUT_DIR / "positional_index.json",
    )
    return engine


def result_card(engine, result, mode, rank):
    """Render one safe, reusable result card."""
    doc_id = result["docID"]
    title = escape(result["title"])
    category = escape(result["category"])
    description = escape(engine.documents[doc_id]["description"])
    icon = CATEGORY_ICONS.get(result["category"], "W")
    if len(description) > 190:
        description = description[:187].rstrip() + "..."

    if mode == "Ranked VSM":
        score = result["score"]
        evidence = f"""
            <div class="score-row"><span>Cosine similarity</span><strong>{score:.6f}</strong></div>
            <div class="score-track"><div class="score-fill" style="width:{min(score * 100, 100):.2f}%"></div></div>
        """
    elif mode == "Exact phrase":
        evidence = f"""
            <div class="evidence-box"><span>Exact positional match</span>
            <code>{escape(str(result['matched_positions']))}</code></div>
        """
    else:
        evidence = f"""
            <div class="evidence-box"><span>Ordered position pairs</span>
            <code>{escape(str(result['matches']))}</code></div>
        """

    st.markdown(
        f"""
        <article class="product-card">
            <div class="card-topline"><span class="rank-chip">#{rank:02d}</span><span class="doc-chip">{escape(doc_id)}</span></div>
            <div class="product-visual"><i></i><b></b><strong>{icon}</strong></div>
            <div class="product-copy">
                <span class="category-label">{category}</span><h3>{title}</h3><p>{description}</p>{evidence}
            </div>
        </article>
        """,
        unsafe_allow_html=True,
    )

    document = engine.documents[doc_id]
    raw_document = (
        "<DOC>\n"
        f"<DOCID>{doc_id}</DOCID>\n"
        f"<CATEGORY>{document['category']}</CATEGORY>\n"
        f"<TITLE>{document['title']}</TITLE>\n"
        f"<TEXT>{document['description']}</TEXT>\n"
        "</DOC>"
    )

    with st.popover(
        f"Open full document · {doc_id}",
        use_container_width=True,
    ):
        st.markdown(f"### {document['title']}")
        st.caption(
            f"Document {doc_id} · {document['category']} · Original corpus entry"
        )
        st.write(document["description"])
        st.code(raw_document, language="xml")


st.set_page_config(
    page_title="THREADS — Clothing Search",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --pink:#ED0F87; --lilac:#E18FE5; --lavender:#AB8BEE;
        --capri:#1BB5FD; --blue:#07329B; --ink:#08133B;
        --muted:#5A6280; --paper:#FBFAFF;
    }
    #MainMenu, footer, header {visibility:hidden}
    .stApp {
        background:radial-gradient(circle at 8% 4%,rgba(225,143,229,.34),transparent 25rem),
        radial-gradient(circle at 96% 34%,rgba(27,181,253,.24),transparent 27rem),
        linear-gradient(145deg,#fffaff 0%,#f3efff 48%,#eef9ff 100%); color:var(--ink)
    }
    .block-container {max-width:1180px;padding:1.25rem 2rem 4rem}
    .brandbar {display:flex;align-items:center;justify-content:space-between;margin-bottom:1.15rem}
    .brand {display:flex;align-items:center;gap:.7rem;color:var(--blue);font-size:1rem;font-weight:900;letter-spacing:.16em}
    .brand-mark {display:grid;place-items:center;width:2.4rem;height:2.4rem;border-radius:.8rem;background:var(--pink);color:white;box-shadow:0 8px 18px rgba(237,15,135,.28)}
    .course-badge {padding:.52rem .8rem;border:1px solid rgba(7,50,155,.14);border-radius:999px;background:rgba(255,255,255,.62);color:var(--blue);font-size:.75rem;font-weight:800;letter-spacing:.08em}
    .hero {position:relative;overflow:hidden;min-height:310px;padding:3.4rem 3.5rem;border-radius:32px;background:linear-gradient(118deg,#061f70 0%,var(--blue) 58%,#164fc9 100%);box-shadow:0 24px 65px rgba(7,50,155,.25);color:white}
    .hero:before,.hero:after {content:"";position:absolute;border-radius:999px}
    .hero:before {width:340px;height:340px;right:-60px;top:-120px;background:linear-gradient(145deg,var(--pink),var(--lilac));opacity:.95}
    .hero:after {width:240px;height:240px;right:180px;bottom:-170px;border:44px solid var(--capri);opacity:.65}
    .hero-copy {position:relative;z-index:2;max-width:670px}
    .eyebrow {display:inline-flex;align-items:center;gap:.5rem;margin-bottom:1.1rem;color:#dff5ff;font-size:.78rem;font-weight:850;letter-spacing:.14em;text-transform:uppercase}
    .eyebrow-dot {width:.55rem;height:.55rem;border-radius:50%;background:var(--pink);box-shadow:0 0 0 6px rgba(237,15,135,.2)}
    .hero h1 {max-width:630px;margin:0;color:white;font-size:clamp(2.6rem,6vw,5rem);line-height:.96;letter-spacing:-.055em;font-weight:900}
    .hero h1 em {color:var(--lilac);font-style:normal}
    .hero p {max-width:580px;margin:1.35rem 0 0;color:rgba(255,255,255,.78);font-size:1.02rem;line-height:1.65}
    .stats-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin:1rem 0 2.15rem}
    .stat-card {padding:1.05rem 1.2rem;border:1px solid rgba(7,50,155,.1);border-radius:18px;background:rgba(255,255,255,.72);box-shadow:0 10px 30px rgba(7,50,155,.07);backdrop-filter:blur(12px)}
    .stat-value {color:var(--blue);font-size:1.45rem;font-weight:900}
    .stat-label {margin-top:.15rem;color:var(--muted);font-size:.76rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}
    .section-kicker {margin-bottom:.25rem;color:var(--pink);font-size:.76rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase}
    .section-title {margin:0 0 1rem;color:var(--ink);font-size:1.8rem;font-weight:900;letter-spacing:-.035em}
    div[role="radiogroup"] {gap:.7rem;margin-bottom:1.25rem}
    div[role="radiogroup"] label {flex:1;justify-content:center;min-height:3.15rem;padding:.65rem 1rem!important;border:1px solid rgba(7,50,155,.13);border-radius:14px;background:rgba(255,255,255,.7);box-shadow:0 7px 18px rgba(7,50,155,.05)}
    div[role="radiogroup"] label:has(input:checked) {border-color:var(--pink);background:linear-gradient(135deg,rgba(237,15,135,.12),rgba(225,143,229,.18));color:var(--blue)}
    div[data-testid="stForm"] {padding:1.45rem;border:1px solid rgba(7,50,155,.11);border-radius:22px;background:rgba(255,255,255,.78);box-shadow:0 15px 42px rgba(7,50,155,.09);backdrop-filter:blur(14px)}
    .stTextInput input,.stNumberInput input {min-height:3.15rem;border:1px solid rgba(7,50,155,.15)!important;border-radius:13px!important;background:#fff!important;color:var(--ink)!important}
    .stTextInput input:focus,.stNumberInput input:focus {border-color:var(--pink)!important;box-shadow:0 0 0 3px rgba(237,15,135,.12)!important}
    .stButton>button,.stFormSubmitButton>button {min-height:3.15rem;border:0;border-radius:13px;background:linear-gradient(120deg,var(--pink),#f344aa);box-shadow:0 11px 24px rgba(237,15,135,.24);color:white;font-weight:850;transition:.18s ease}
    .stButton>button:hover,.stFormSubmitButton>button:hover {background:linear-gradient(120deg,#d80a78,var(--pink));box-shadow:0 15px 30px rgba(237,15,135,.3);color:white;transform:translateY(-1px)}
    div[data-testid="stPopover"]>button {margin-top:-.55rem;margin-bottom:1rem;border:1px solid rgba(7,50,155,.13);border-radius:13px;background:rgba(255,255,255,.86);box-shadow:0 9px 22px rgba(7,50,155,.07);color:var(--blue);font-weight:850}
    div[data-testid="stPopover"]>button:hover {border-color:var(--pink);background:rgba(237,15,135,.07);color:var(--pink)}
    .tip-line {margin:.8rem 0 0;color:var(--muted);font-size:.82rem}.tip-line strong{color:var(--blue)}
    .results-header {display:flex;align-items:end;justify-content:space-between;margin:2.6rem 0 1rem}
    .results-header h2 {margin:0;color:var(--ink);font-size:1.75rem;font-weight:900;letter-spacing:-.035em}
    .results-count {color:var(--blue);font-size:.82rem;font-weight:800}
    .product-card {position:relative;min-height:410px;margin-bottom:1.1rem;overflow:hidden;border:1px solid rgba(7,50,155,.1);border-radius:24px;background:rgba(255,255,255,.84);box-shadow:0 15px 42px rgba(7,50,155,.09);transition:.2s ease}
    .product-card:hover {transform:translateY(-4px);box-shadow:0 22px 48px rgba(7,50,155,.14)}
    .card-topline {position:absolute;z-index:3;top:.9rem;left:.9rem;right:.9rem;display:flex;justify-content:space-between}
    .rank-chip,.doc-chip {padding:.35rem .62rem;border-radius:999px;font-size:.7rem;font-weight:900}.rank-chip{background:var(--pink);color:white}.doc-chip{background:rgba(255,255,255,.86);color:var(--blue)}
    .product-visual {position:relative;display:grid;place-items:center;height:165px;overflow:hidden;background:linear-gradient(130deg,var(--lilac),var(--lavender) 48%,var(--capri))}
    .product-visual strong {position:relative;z-index:2;display:grid;place-items:center;width:78px;height:78px;border:2px solid rgba(255,255,255,.65);border-radius:26px;background:rgba(7,50,155,.88);box-shadow:0 14px 32px rgba(7,50,155,.28);color:white;font-size:1.2rem;font-weight:950}
    .product-visual i,.product-visual b {position:absolute;border:1px solid rgba(255,255,255,.5);border-radius:50%}.product-visual i{width:190px;height:190px}.product-visual b{width:290px;height:110px;transform:rotate(-14deg)}
    .product-copy {padding:1.25rem 1.3rem 1.4rem}.category-label{color:var(--pink);font-size:.7rem;font-weight:900;letter-spacing:.1em;text-transform:uppercase}
    .product-copy h3 {min-height:2.8rem;margin:.35rem 0 .55rem;color:var(--ink);font-size:1.08rem;line-height:1.3;font-weight:900;letter-spacing:-.02em}
    .product-copy p {min-height:4.1rem;margin:0;color:var(--muted);font-size:.8rem;line-height:1.55}
    .score-row {display:flex;justify-content:space-between;margin-top:1rem;color:var(--blue);font-size:.74rem;font-weight:800}
    .score-track {height:7px;margin-top:.45rem;overflow:hidden;border-radius:99px;background:#e9e5f5}.score-fill{height:100%;min-width:7px;border-radius:inherit;background:linear-gradient(90deg,var(--pink),var(--capri))}
    .evidence-box {margin-top:.9rem;padding:.72rem .78rem;border-left:3px solid var(--capri);border-radius:8px;background:rgba(27,181,253,.08)}
    .evidence-box span {display:block;margin-bottom:.35rem;color:var(--blue);font-size:.67rem;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.evidence-box code{white-space:normal;color:#2c3560;font-size:.7rem}
    .empty-state {margin-top:2rem;padding:3rem 1.5rem;border:1px dashed rgba(7,50,155,.2);border-radius:24px;background:rgba(255,255,255,.52);text-align:center}
    .empty-icon {display:grid;place-items:center;width:58px;height:58px;margin:0 auto .8rem;border-radius:18px;background:linear-gradient(135deg,var(--pink),var(--lavender));color:white;font-size:1.45rem}
    .empty-state h3{margin:0;color:var(--ink)}.empty-state p{margin:.45rem 0 0;color:var(--muted)}
    .site-footer {margin-top:3rem;padding-top:1.2rem;border-top:1px solid rgba(7,50,155,.1);color:var(--muted);font-size:.76rem;text-align:center}
    @media(max-width:760px){.block-container{padding:1rem 1rem 3rem}.hero{min-height:340px;padding:2.4rem 1.5rem}.hero:before{right:-180px;opacity:.65}.hero h1{font-size:2.65rem}.stats-grid{grid-template-columns:1fr}.course-badge{display:none}div[role="radiogroup"]{flex-direction:column}.product-card{min-height:auto}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="brandbar"><div class="brand"><span class="brand-mark">✦</span> THREADS</div><div class="course-badge">CSD358 · INFORMATION RETRIEVAL</div></div>
    <section class="hero"><div class="hero-copy">
        <div class="eyebrow"><span class="eyebrow-dot"></span> Intelligent apparel discovery</div>
        <h1>Find your next <em>favourite.</em></h1>
        <p>Explore 100 clothing products with ranked retrieval, exact phrase matching, and ordered positional search.</p>
    </div></section>
    """,
    unsafe_allow_html=True,
)

if not DATA_PATH.exists():
    st.error("The corpus is missing. Add the official file at data/corpus_100.txt.")
    st.stop()

engine = load_engine()
category_count = len({doc["category"] for doc in engine.documents.values()})
st.markdown(
    f"""
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-value">{engine.N}</div><div class="stat-label">Products indexed</div></div>
        <div class="stat-card"><div class="stat-value">{category_count}</div><div class="stat-label">Clothing categories</div></div>
        <div class="stat-card"><div class="stat-value">{len(engine.positional_index)}</div><div class="stat-label">Dictionary terms</div></div>
    </div><div class="section-kicker">Search studio</div><h2 class="section-title">Choose how you want to search</h2>
    """,
    unsafe_allow_html=True,
)

mode = st.radio("Search mode", ["Ranked VSM", "Exact phrase", "Ordered proximity"], horizontal=True, label_visibility="collapsed")
results = None
search_label = ""

if mode == "Ranked VSM":
    with st.form("ranked-search", border=False):
        query = st.text_input("What are you looking for?", placeholder="Try: breathable cotton shirt")
        submitted = st.form_submit_button("Search collection →", use_container_width=True)
    st.markdown('<p class="tip-line"><strong>Best for:</strong> natural queries ranked with lnc.ltc cosine similarity.</p>', unsafe_allow_html=True)
    if submitted:
        search_label = query.strip()
        results = engine.ranked_search(search_label, limit=10) if search_label else []

elif mode == "Exact phrase":
    with st.form("phrase-search", border=False):
        phrase = st.text_input("Enter words in their exact order", placeholder="Try: stretch denim")
        submitted = st.form_submit_button("Find exact matches →", use_container_width=True)
    st.markdown('<p class="tip-line"><strong>Try:</strong> cotton shirt · festive wear · regular fit · high waist</p>', unsafe_allow_html=True)
    if submitted:
        search_label = phrase.strip()
        results = engine.phrase_search(search_label) if search_label else []

else:
    with st.form("proximity-search", border=False):
        col1, col2, col3 = st.columns([1.2, 1.2, .65])
        with col1:
            first_term = st.text_input("First term", placeholder="cotton")
        with col2:
            second_term = st.text_input("Second term", placeholder="shirt")
        with col3:
            k = st.number_input("Within k", min_value=1, max_value=20, value=3)
        submitted = st.form_submit_button("Check ordered proximity →", use_container_width=True)
    st.markdown('<p class="tip-line"><strong>Meaning:</strong> the first term must occur before the second within k token positions.</p>', unsafe_allow_html=True)
    if submitted:
        first_term, second_term = first_term.strip(), second_term.strip()
        search_label = f"{first_term} WITHIN/{int(k)} {second_term}"
        results = engine.proximity_search(first_term, second_term, int(k)) if first_term and second_term else []

if results is not None:
    st.markdown(
        f'<div class="results-header"><h2>Results for “{escape(search_label)}”</h2><span class="results-count">{len(results)} MATCH{"ES" if len(results) != 1 else ""}</span></div>',
        unsafe_allow_html=True,
    )
    if results:
        columns = st.columns(2)
        for index, result in enumerate(results, start=1):
            with columns[(index - 1) % 2]:
                result_card(engine, result, mode, index)
    else:
        st.markdown('<div class="empty-state"><div class="empty-icon">⌕</div><h3>No matching pieces found</h3><p>Try broader terms, check the spelling, or choose another search mode.</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="empty-state"><div class="empty-icon">✦</div><h3>Your curated results will appear here</h3><p>Choose a mode, enter a query, and explore the indexed collection.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="site-footer">THREADS · Built with an inverted index, positional postings, and lnc.ltc ranking</div>', unsafe_allow_html=True)
