import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

from nltk.stem import PorterStemmer


class ClothingSearchEngine:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.documents = {}
        self.positional_index = defaultdict(dict)
        self.document_norms = {}
        self.N = 0

    def preprocess(self, text):
        """
        Preprocessing policy for the tagged corpus:
        1. Lowercase text.
        2. Remove apostrophes so Men's -> Mens.
        3. Treat punctuation and hyphen as token boundaries.
        4. Extract alphanumeric tokens.
        5. Stem via Porter stemming.
        6. Keep stop words to preserve exact positional semantics.
        """
        text = str(text).lower().replace("'", "")
        tokens = re.findall(r"[a-z0-9]+", text)
        return [self.stemmer.stem(token) for token in tokens]

    @staticmethod
    def _extract_field(document_block, field_name):
        pattern = rf"<{field_name}>(.*?)</{field_name}>"
        match = re.search(pattern, document_block, flags=re.DOTALL)
        if not match:
            raise ValueError(f"Missing <{field_name}> field in a document.")
        return match.group(1).strip()

    def build_index(self, corpus_path):
        """
        Read the tagged corpus used by this assignment:
            <DOC> ... <DOCID>D001</DOCID> ... </DOC>
        """
        path = Path(corpus_path)

        self.documents = {}
        self.positional_index = defaultdict(dict)
        self.document_norms = {}

        corpus = path.read_text(encoding="utf-8")
        document_blocks = re.findall(r"<DOC>\s*(.*?)\s*</DOC>", corpus, flags=re.DOTALL)

        if not document_blocks:
            raise ValueError("No <DOC> records were found in the corpus.")

        for block in document_blocks:
            doc_id = self._extract_field(block, "DOCID")
            category = self._extract_field(block, "CATEGORY")
            title = self._extract_field(block, "TITLE")
            description = self._extract_field(block, "TEXT")

            if doc_id in self.documents:
                raise ValueError(f"Duplicate document ID: {doc_id}")

            self.documents[doc_id] = {
                "title": title,
                "category": category,
                "description": description,
            }

            # Index TEXT only to avoid double-counting title words.
            tokens = self.preprocess(description)
            term_positions = defaultdict(list)
            for position, term in enumerate(tokens):
                term_positions[term].append(position)
            for term, positions in term_positions.items():
                self.positional_index[term][doc_id] = positions

        self.N = len(self.documents)

        if self.N != 100:
            raise ValueError(f"Expected 100 documents, but found {self.N}.")

        self._calculate_document_norms()

    def _calculate_document_norms(self):
        """
        Calculate lnc document-vector lengths.
        Document weight = 1 + log10(tf), without IDF.
        """
        squared_lengths = defaultdict(float)

        for postings in self.positional_index.values():
            for doc_id, positions in postings.items():
                tf = len(positions)
                weight = 1 + math.log10(tf)
                squared_lengths[doc_id] += weight ** 2

        self.document_norms = {
            doc_id: math.sqrt(value) if value > 0 else 0.0
            for doc_id, value in squared_lengths.items()
        }

    def get_dictionary(self):
        dictionary = {}
        for term in sorted(self.positional_index):
            postings = self.positional_index[term]
            dictionary[term] = {
                "df": len(postings),
                "postings": [
                    {"docID": doc_id, "tf": len(positions)}
                    for doc_id, positions in sorted(postings.items())
                ],
            }
        return dictionary

    def get_positional_dictionary(self):
        dictionary = {}
        for term in sorted(self.positional_index):
            postings = self.positional_index[term]
            dictionary[term] = {
                "df": len(postings),
                "postings": [
                    {
                        "docID": doc_id,
                        "tf": len(positions),
                        "positions": positions,
                    }
                    for doc_id, positions in sorted(postings.items())
                ],
            }
        return dictionary

    def save_indexes(self, dictionary_path, positional_path):
        os.makedirs(os.path.dirname(dictionary_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(positional_path) or ".", exist_ok=True)

        with open(dictionary_path, "w", encoding="utf-8") as file:
            json.dump(self.get_dictionary(), file, indent=2)

        with open(positional_path, "w", encoding="utf-8") as file:
            json.dump(self.get_positional_dictionary(), file, indent=2)

    def ranked_search(self, query, limit=10):
        query_terms = self.preprocess(query)
        query_tf = Counter(query_terms)
        query_weights = {}

        for term, tf in query_tf.items():
            if term not in self.positional_index:
                continue
            df = len(self.positional_index[term])
            idf = math.log10(self.N / df) if df > 0 else 0.0
            query_weights[term] = (1 + math.log10(tf)) * idf

        query_norm = math.sqrt(sum(weight ** 2 for weight in query_weights.values()))
        if query_norm == 0:
            return []

        scores = defaultdict(float)

        for term, query_weight in query_weights.items():
            normalized_query_weight = query_weight / query_norm
            for doc_id, positions in self.positional_index[term].items():
                tf = len(positions)
                document_weight = 1 + math.log10(tf)
                document_norm = self.document_norms.get(doc_id, 0.0)
                if document_norm == 0:
                    continue
                normalized_document_weight = document_weight / document_norm
                scores[doc_id] += normalized_document_weight * normalized_query_weight

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        results = []
        for doc_id, score in ranked[:limit]:
            document = self.documents[doc_id]
            results.append({
                "docID": doc_id,
                "title": document["title"],
                "category": document["category"],
                "score": score,
            })
        return results

    def phrase_search(self, phrase):
        terms = self.preprocess(phrase)
        if not terms:
            return []
        if any(term not in self.positional_index for term in terms):
            return []

        candidate_documents = set(self.positional_index[terms[0]].keys())
        for term in terms[1:]:
            candidate_documents &= set(self.positional_index[term].keys())

        results = []
        for doc_id in sorted(candidate_documents):
            first_term_positions = self.positional_index[terms[0]][doc_id]
            remaining_position_sets = [
                set(self.positional_index[term][doc_id])
                for term in terms[1:]
            ]

            phrase_starts = []
            for start in first_term_positions:
                matches = all(
                    start + offset in remaining_position_sets[offset - 1]
                    for offset in range(1, len(terms))
                )
                if matches:
                    phrase_starts.append(start)

            if phrase_starts:
                results.append({
                    "docID": doc_id,
                    "title": self.documents[doc_id]["title"],
                    "category": self.documents[doc_id]["category"],
                    "phrase_starts": phrase_starts,
                    "matched_positions": [
                        list(range(start, start + len(terms)))
                        for start in phrase_starts
                    ],
                })

        return results

    def proximity_search(self, first_term, second_term, k):
        processed_first = self.preprocess(first_term)
        processed_second = self.preprocess(second_term)

        if len(processed_first) != 1 or len(processed_second) != 1:
            raise ValueError("Each side of a proximity query must be one term.")

        term1 = processed_first[0]
        term2 = processed_second[0]

        if term1 not in self.positional_index or term2 not in self.positional_index:
            return []

        candidate_documents = (
            set(self.positional_index[term1].keys())
            & set(self.positional_index[term2].keys())
        )

        results = []
        for doc_id in sorted(candidate_documents):
            positions1 = self.positional_index[term1][doc_id]
            positions2 = self.positional_index[term2][doc_id]
            matching_pairs = []

            for first_position in positions1:
                for second_position in positions2:
                    distance = second_position - first_position
                    if 0 < distance <= k:
                        matching_pairs.append({
                            "first_position": first_position,
                            "second_position": second_position,
                            "distance": distance,
                        })

            if matching_pairs:
                results.append({
                    "docID": doc_id,
                    "title": self.documents[doc_id]["title"],
                    "category": self.documents[doc_id]["category"],
                    "matches": matching_pairs,
                })

        return results

    def recommend_documents(self, seed_doc_ids, exclude_doc_ids=None, limit=4):
        """Recommend unseen documents similar to the retrieved results.

        The first three retrieved documents are represented as normalized
        log-TF-IDF vectors and averaged into a centroid. Remaining documents
        are ranked by cosine similarity to that centroid.
        """
        seeds = [doc_id for doc_id in seed_doc_ids if doc_id in self.documents][:3]
        if not seeds or limit <= 0:
            return []

        excluded = set(exclude_doc_ids or [])
        excluded.update(seeds)
        vectors = {doc_id: {} for doc_id in self.documents}
        squared_norms = defaultdict(float)

        for term, postings in self.positional_index.items():
            df = len(postings)
            idf = math.log10(self.N / df) if df else 0.0
            if idf == 0:
                continue

            for doc_id, positions in postings.items():
                weight = (1 + math.log10(len(positions))) * idf
                vectors[doc_id][term] = weight
                squared_norms[doc_id] += weight ** 2

        normalized_vectors = {}
        for doc_id, vector in vectors.items():
            norm = math.sqrt(squared_norms[doc_id])
            normalized_vectors[doc_id] = (
                {term: weight / norm for term, weight in vector.items()}
                if norm
                else {}
            )

        centroid = defaultdict(float)
        for doc_id in seeds:
            for term, weight in normalized_vectors[doc_id].items():
                centroid[term] += weight / len(seeds)

        centroid_norm = math.sqrt(sum(weight ** 2 for weight in centroid.values()))
        if centroid_norm == 0:
            return []

        scored = []
        for doc_id, vector in normalized_vectors.items():
            if doc_id in excluded or not vector:
                continue

            score = sum(
                weight * centroid.get(term, 0.0)
                for term, weight in vector.items()
            ) / centroid_norm
            if score > 0:
                scored.append((doc_id, score))

        scored.sort(key=lambda item: (-item[1], item[0]))
        return [
            {
                "docID": doc_id,
                "title": self.documents[doc_id]["title"],
                "category": self.documents[doc_id]["category"],
                "score": score,
            }
            for doc_id, score in scored[:limit]
        ]


if __name__ == "__main__":
    engine = ClothingSearchEngine()
    engine.build_index("data/corpus_100.txt")
    print("Documents:", engine.N)
    print("Dictionary terms:", len(engine.positional_index))
    engine.save_indexes("outputs/dictionary.json", "outputs/positional_index.json")
