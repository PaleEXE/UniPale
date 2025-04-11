# import 'Counter' to count term occurrence in a document
import glob
from collections import Counter

import numpy as np
import pandas as pd

# import utilies to reduce code duplication (DRY principle)
from utils import *
from incidence_matrix import IncidenceMatrix


# use inheritance to create 'CountMatrix' since a lot of features are common between the two classes
class CountMatrix(IncidenceMatrix):
    # same building method but insert count in the matrix instead of ones and zeros
    def build(self) -> None:
        incidence = dict()
        for doc_num, file_path in enumerate(self.collection):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                words = nltk.word_tokenize(content)

            words_count = Counter(normalize_list(words))

            for word, count in words_count.items():
                if word not in incidence:
                    incidence[word] = np.zeros(self.num_docs, dtype=np.int64)

                incidence[word][doc_num] = count

        self.matrix = pd.DataFrame.from_dict(incidence, orient='index', columns=get_files_names(self.collection))
        self.matrix.sort_index(inplace=True)

    # search using natural language and rank retrieved documents based on term frequency (trivial solution)
    def search(self, query: str) -> list[list[str, int]]:
        scores = [[name, 0] for name in self.matrix.columns]
        query_list = nltk.word_tokenize(query)

        for i, doc in enumerate(self.matrix.columns):
            for term in query_list:
                term = normalize(term)
                scores[i][1] += self.matrix[doc].get(term, 0)

        scores = [score for score in scores if score[1] != 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


if __name__ == '__main__':
    ct = CountMatrix.from_folder('../pale_ir/songs/')
    print(ct.search('love CaRs'))
    print(ct.search('Messi lady'))
    print(ct.search('call'))
    ct.save('data/count_matrix.csv')

    ct2 = CountMatrix.load('data/count_matrix.csv')
    print(ct2.search('call'))
