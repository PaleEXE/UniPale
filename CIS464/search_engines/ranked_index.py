from collections import Counter
import math

from .utils import *
from .inverted_index import InvertedIndex


class RankedIndex(InvertedIndex):
    def build(self):
        for doc_num, file_path in enumerate(self.collection):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                terms = nltk.word_tokenize(content)

            terms = Counter(normalize_list(terms))

            for term, count in terms.items():
                if term not in self.index:
                    self.index[term] = []

                self.index[term].append((doc_num, count))

    def search(self, query: str) -> list[str, float]:
        scores = [[name, 0.] for name in self.doc_names]
        query_list = normalize_list(nltk.word_tokenize(query))

        for term in query_list:
            term = normalize(term)
            for doc_num, count in self.index.get(term, []):
                scores[doc_num][1] += self.score(term, count)

        scores = [score for score in scores if score[1] != 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def score(self, term: str, count: int) -> float:
        if term not in self.index:
            return 0

        tf = math.log10(count) + 1 if count > 0 else 0
        idf = math.log10(self.num_docs / len(self.index[term]))

        w = tf * idf
        return w
