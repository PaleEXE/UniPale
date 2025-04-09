# glob and os used to interact with folders
import glob

# libraries that help build the project
import numpy as np
import pandas as pd

# some functions that will be used across all projects
from utils import *


# class to encapsulate logic and data
class IncidenceMatrix:
    # initial data members to compute the matrix later
    def __init__(self, collection_path: str):
        self.collection = glob.glob(collection_path + "*.txt")
        self.matrix = pd.DataFrame([])
        self.num_docs = len(self.collection)

    # creat the matrix
    def build(self) -> None:
        incidence = dict()

        for doc_num, file_path in enumerate(self.collection):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                terms = set(nltk.word_tokenize(content))

            terms = normalize_list(terms)

            for term in terms:
                if term not in incidence:
                    incidence[term] = np.zeros(self.num_docs, dtype=np.int8)  # Add a row of zeros when a new term occurred

                incidence[term][doc_num] = 1

        self.matrix = pd.DataFrame.from_dict(incidence, orient="index", columns=get_files_names(self.collection))
        self.matrix.sort_index(inplace=True)

    # search in the matrix by applying the same preprocessing that used when building on the query
    # return list of documents which term was observed into it
    def search(self, query: str) -> list[str]:
        query_list = nltk.word_tokenize(query)
        postfix_query = infix_to_postfix(query_list)
        result = self.__solve(postfix_query)
        return self.matrix.columns[result == 1].tolist()

    # apply bitwise operations based on the desired query
    def __solve(self, postfix_query: list[str]) -> pd.Series:
        solve_stack = []

        for token in postfix_query:
            if token not in OPERATIONS and token.isalnum():
                token = normalize(token)
                solve_stack.append(self.get(token))
                continue

            if token == 'NOT':
                solve_stack[-1] = ~ solve_stack[-1]
                continue

            right = solve_stack.pop()
            left = solve_stack.pop()

            if token == 'AND':
                solve_stack.append(left & right)
            elif token == 'OR':
                solve_stack.append(left | right)

        if len(solve_stack) == 1:
            return solve_stack[0]

        raise Exception("Invalid query")

    # get term vector or vector of zeros if it does not exist in the matrix
    def get(self, term) -> np.ndarray:
        if term in self.matrix.index:
            return self.matrix.loc[term].values

        return np.zeros(self.num_docs, dtype=np.int8)


if __name__ == "__main__":
    inc = IncidenceMatrix("../pale_ir/songs/")
    inc.build()
    print(inc.search('love AND CaRs'))
    print(inc.search('Messi OR lady'))
    print(inc.search('Call AND NOT phone'))

