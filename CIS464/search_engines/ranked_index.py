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
                if count == 0:
                    continue

                scores[doc_num][1] += round(self.score(term, doc_num), 5)

        scores = [score for score in scores if score[1] != 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    @staticmethod
    def binary_search(list0: list, num: int) -> int:
        low = 0
        high = len(list0) - 1

        while low <= high:
            mid = (high + low) // 2
            if list0[mid][0] < num:
                high = mid - 1
            elif list0[mid][0] > num:
                low = mid + 1
            else:
                return mid

        return -1

    def score(self, term: str, doc_num: int) -> float:
        if term not in self.index:
            return 0

        doc_position = RankedIndex.binary_search(self.index[term], doc_num)
        tf = self.index[term][doc_position][1]

        idf = len(self.index[term])

        w = (math.log10(tf) + 1) * math.log10(self.num_docs / idf)
        return w
