from collections import Counter, defaultdict
import glob
import os
import math
import json
from sortedcontainers import SortedKeyList
from typing import DefaultDict, List, Tuple, Dict

from document import Document


class InvertedIndex:
    def __init__(self) -> None:
        self.documents_map: Dict[int, str] = {}
        self.stem_index: DefaultDict[str, SortedKeyList[Tuple[int, int]]] = defaultdict(
                lambda: SortedKeyList(key=lambda x: x[0])
        )
        self.word_index: DefaultDict[str, SortedKeyList[Tuple[int, int]]] = defaultdict(
                lambda: SortedKeyList(key=lambda x: x[0])
        )
        self.doc_frequencies: Dict[str, int] = {}  # To store document frequency of each term

    def add_document(self, doc: Document) -> None:
        doc_id = doc.get_id()
        self.documents_map[doc_id] = doc.path

        for word, count in doc.word_counter.items():
            self.word_index[word].add((doc_id, count))
            self.doc_frequencies[word] = self.doc_frequencies.get(word, 0) + 1

        for stem, count in doc.stem_counter.items():
            self.stem_index[stem].add((doc_id, count))
            self.doc_frequencies[stem] = self.doc_frequencies.get(stem, 0) + 1

    def from_folder(self, folder: str) -> None:
        for file in glob.glob(os.path.join(folder, "*.txt")):
            doc = Document(file, len(self.documents_map))
            self.add_document(doc)

    def search(self, query: str) -> List[Tuple[int, float]]:
        query = query.lower()

        # Separate search for stem and word
        stem_results = self._search_for_terms(Document.compute_stem_counter(query.split()), use_stem=True)
        word_results = self._search_for_terms(Counter(query.split()), use_stem=False)

        # Combine the results by adding the scores
        combined_scores: Dict[int, float] = defaultdict(float)

        # Add stem search results
        for doc_id, score in stem_results:
            combined_scores[doc_id] += score

        # Add word search results
        for doc_id, score in word_results:
            combined_scores[doc_id] += score

        return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    def _search_for_terms(self, query_terms: Dict[str, int], use_stem: bool) -> List[Tuple[int, float]]:
        """Helper method to search for individual terms in the index."""
        index = self.stem_index if use_stem else self.word_index
        num_docs = len(self.documents_map)
        scores: Dict[int, float] = defaultdict(float)

        for term, query_count in query_terms.items():
            if term not in self.doc_frequencies:
                continue  # Skip terms that don't exist in the index

            df = self.doc_frequencies[term]
            idf = math.log((num_docs + 1) / (df + 1)) + 1  # Smoothed IDF

            for doc_id, term_freq in index[term]:
                tf = 1 + math.log(term_freq)  # Log-scaled TF
                scores[doc_id] += tf * idf * query_count

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def save_to_json(self, file_path: str) -> None:
        data = {
            "documents_map":   {str(k): v for k, v in self.documents_map.items()},  # Convert keys to strings
            "stem_index":      {k: list(v) for k, v in self.stem_index.items()},  # Convert SortedKeyList to list
            "word_index":      {k: list(v) for k, v in self.word_index.items()},
            "doc_frequencies": self.doc_frequencies,
        }
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @classmethod
    def load_from_json(cls, file_path: str) -> "InvertedIndex":
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        instance = cls()
        instance.documents_map = data["documents_map"]
        instance.stem_index = defaultdict(
                lambda: SortedKeyList(key=lambda x: x[0]),
                {k: SortedKeyList(v, key=lambda x: x[0]) for k, v in data["stem_index"].items()}
        )
        instance.word_index = defaultdict(
                lambda: SortedKeyList(key=lambda x: x[0]),
                {k: SortedKeyList(v, key=lambda x: x[0]) for k, v in data["word_index"].items()}
        )
        instance.doc_frequencies = data["doc_frequencies"]
        return instance

    def get_doc(self, doc_id: str) -> str:
        if x := self.documents_map.get(doc_id):
            return x

        return self.documents_map.get(str(doc_id))

    def print_scores(self, scores: list[Tuple[int, float]]) -> None:
        for doc_id, score in scores:
            song = self.get_doc(doc_id).split('\\')[-1].replace('.txt', '')
            print(f"{song:<40}{score:.3}")

        print()
