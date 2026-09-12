from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from search_engine import ClothingSearchEngine


def test_search_engine_pipeline():
    corpus_path = Path(__file__).resolve().parent / "data" / "corpus_100.txt"
    engine = ClothingSearchEngine()
    engine.build_index(str(corpus_path))

    assert engine.N == 100, f"Expected 100 docs, found {engine.N}"
    assert "cotton" in engine.positional_index
    assert "shirt" in engine.positional_index
    assert "stretch" in engine.positional_index
    assert "denim" in engine.positional_index

    ranked = engine.ranked_search("cotton shirt", limit=5)
    assert ranked, "Expected ranked retrieval results for 'cotton shirt'"

    phrase_results = engine.phrase_search("stretch denim")
    assert phrase_results, "Expected exact phrase matches for 'stretch denim'"

    proximity = engine.proximity_search("cotton", "shirt", 3)
    assert proximity, "Expected proximity matches within distance 3"

    nonexistent = engine.ranked_search("nonexistentfabricxyz", limit=5)
    assert nonexistent == [], "A missing term should return no ranked results"

    dictionary = engine.get_dictionary()
    assert "cotton" in dictionary
    assert "denim" in dictionary

    print("All tests passed.")


if __name__ == "__main__":
    test_search_engine_pipeline()
