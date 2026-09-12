from pathlib import Path

from search_engine import ClothingSearchEngine


ROOT = Path(__file__).resolve().parent
CORPUS_PATH = ROOT / "data" / "corpus_100.txt"


def display_ranked_results(engine, query):
    """Display up to 10 VSM results."""
    results = engine.ranked_search(query, limit=10)

    print(f'\nFree-text query: "{query}"')

    if not results:
        print("No matching documents found.")
        return

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['docID']} | "
            f"{result['title']} | "
            f"Category: {result['category']} | "
            f"Score: {result['score']:.6f}"
        )


def display_phrase_results(engine, phrase):
    """Display exact phrase matches and their positions."""
    results = engine.phrase_search(phrase)

    print(f'\nExact phrase: "{phrase}"')

    if not results:
        print("No exact phrase matches found.")
        return

    for result in results[:10]:
        print(
            f"{result['docID']} | "
            f"{result['title']} | "
            f"Positions: {result['matched_positions']}"
        )


def display_proximity_results(
    engine,
    first_term,
    second_term,
    k,
):
    """Display ordered proximity matches and positions."""
    results = engine.proximity_search(
        first_term,
        second_term,
        k,
    )

    print(
        f"\nProximity query: "
        f"{first_term} WITHIN/{k} {second_term}"
    )

    if not results:
        print("No proximity matches found.")
        return

    for result in results[:10]:
        print(
            f"{result['docID']} | "
            f"{result['title']} | "
            f"Position pairs: {result['matches']}"
        )


def run_mandatory_tests(engine):
    """
    Run the number of queries required by the assignment.

    These are input queries, not hard-coded expected document IDs.
    The engine calculates every result dynamically.
    """
    free_text_queries = [
        "cotton shirt",
        "blue denim jeans",
        "festive kurta",
        "winter jacket",
        "high waist leggings",
        "regular fit shirt",
        "breathable fabric",
        "zip closure hoodie",
        "summer dress",
        "casual sweatshirt",
        "nonexistentfabricxyz",
    ]

    phrase_queries = [
        "cotton shirt",
        "stretch denim",
        "festive wear",
        "winter wear",
        "regular fit",
        "breathable fabric",
        "high waist",
    ]

    proximity_queries = [
        ("cotton", "shirt", 3),
        ("stretch", "denim", 4),
        ("winter", "wear", 2),
    ]

    print("\n" + "=" * 70)
    print("MANDATORY FREE-TEXT TESTS")
    print("=" * 70)

    for query in free_text_queries:
        display_ranked_results(engine, query)

    print("\n" + "=" * 70)
    print("MANDATORY EXACT-PHRASE TESTS")
    print("=" * 70)

    for phrase in phrase_queries:
        display_phrase_results(engine, phrase)

    print("\n" + "=" * 70)
    print("MANDATORY PROXIMITY TESTS")
    print("=" * 70)

    for first_term, second_term, k in proximity_queries:
        display_proximity_results(
            engine,
            first_term,
            second_term,
            k,
        )


def interactive_search(engine):
    """Allow the user to enter searches manually."""
    while True:
        print("\nChoose a search mode:")
        print("1. Free-text VSM search")
        print("2. Exact phrase search")
        print("3. Ordered proximity search")
        print("4. Return to main menu")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            query = input(
                "Enter a free-text clothing query: "
            ).strip()

            display_ranked_results(engine, query)

        elif choice == "2":
            phrase = input(
                "Enter an exact phrase: "
            ).strip()

            display_phrase_results(engine, phrase)

        elif choice == "3":
            first_term = input("Enter the first term: ").strip()
            second_term = input("Enter the second term: ").strip()

            try:
                k = int(input("Enter the value of k: ").strip())

                if k < 1:
                    print("k must be at least 1.")
                    continue

                display_proximity_results(
                    engine,
                    first_term,
                    second_term,
                    k,
                )

            except ValueError:
                print("Please enter a whole number for k.")

        elif choice == "4":
            return

        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")


def main():
    engine = ClothingSearchEngine()
    engine.build_index(CORPUS_PATH)

    print("Clothing Search Engine")
    print(f"Loaded documents: {engine.N}")
    print(f"Dictionary terms: {len(engine.positional_index)}")

    while True:
        print("\nMain menu:")
        print("1. Run all mandatory assignment tests")
        print("2. Enter queries manually")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            run_mandatory_tests(engine)

        elif choice == "2":
            interactive_search(engine)

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid choice. Enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
