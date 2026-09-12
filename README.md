# Clothing Search Engine

This project implements a compact retrieval system for a clothing dataset. It uses one shared preprocessing pipeline, one positional index, and derives the ordinary dictionary and VSM statistics from that same structure.

## Dataset format

The assignment corpus uses tagged XML-style blocks:

```xml
<DOC>
  <DOCID>D001</DOCID>
  <CATEGORY>T-Shirt</CATEGORY>
  <TITLE>Men's Cotton Crew Neck T-Shirt - Black</TITLE>
  <TEXT>Men's Cotton Crew Neck T-Shirt - Black. Made from soft cotton and breathable fabric for everyday comfort.</TEXT>
</DOC>
```

The program uses this tagged corpus as its only data source.

## Preprocessing policy

The engine uses:

- Lowercase conversion
- Apostrophe removal (`Men's` -> `mens`)
- Hyphen and punctuation treated as separators
- Alphanumeric token extraction
- Porter stemming
- Stop words retained

Keeping stop words is intentional because phrase and proximity matching depend on original token positions. If words such as "with" or "for" are removed, the positional indices no longer reflect the original sequence, and exact phrase checks can become incorrect.

Example:

- Original sequence: `cotton with shirt`
- Removing `with` can make `cotton shirt` appear adjacent even when it was not an exact phrase in the original text.

## Why only TEXT is indexed

The corpus contains titles in both `<TITLE>` and `<TEXT>`, so indexing the concatenated text would double-count title words. This would inflate term frequencies and distort the VSM ranking scores.

Therefore:

- Store `TITLE` and `CATEGORY` for result display.
- Index only `TEXT` for retrieval.
- Use the same positional postings for ranked retrieval, phrase matching, and proximity matching.

## Retrieval formulas

Document term weight (lnc):

$$w_{d,t} = 1 + \log_{10}(tf_{d,t})$$

Query term weight (ltc):

$$w_{q,t} = (1 + \log_{10}(tf_{q,t})) \times \log_{10}(N/df_t)$$

Cosine score:

$$score(d,q) = \sum_{t \in q \cap d} \frac{w_{d,t}}{|d|} \cdot \frac{w_{q,t}}{|q|}$$

## Project structure

```text
clothing-search-engine/
├── data/
│   ├── corpus_100.txt
├── outputs/
│   ├── dictionary.json
│   ├── positional_index.json
│   └── test_results.txt
├── search_engine.py
├── app.py
├── tests.py
├── requirements.txt
├── README.md
└── screenshots/
```

## Run the project

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Keep the tagged corpus at `data/corpus_100.txt`.

3. Run the tests:

```bash
python tests.py
```

4. Launch the Streamlit app:

```bash
streamlit run app.py
```

## Supported retrieval modes

- Ranked VSM retrieval
- Exact phrase search using positional postings
- Ordered proximity search with distance `k`

## Git workflow note

The assignment instructions say to save/progress to Git periodically, typically by committing and pushing every couple of hours. A normal cycle is:

```bash
git status
git add .
git commit -m "Implemented corpus parser and preprocessing"
git push
```

This keeps the project history visible and helps ensure the final repository state is submitted correctly.
