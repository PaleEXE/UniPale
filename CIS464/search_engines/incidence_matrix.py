# glob and os used to interact with folders
import glob

# libraries that help build the project
import numpy as np
import pandas as pd

# some functions that will be used across all projects
from .utils import *


# class to encapsulate logic and data
class IncidenceMatrix:
    # initial data members to compute the matrix later
    def __init__(self):
        self.collection = []
        self.matrix = pd.DataFrame([])
        self.num_docs = 0

    # create an object from a folder
    @classmethod
    def from_folder(cls, folder_path: str):  # I didn't add return type for compatibility issues with py3.11 <
        obj = cls()
        obj.collection = glob.glob(folder_path + '*.txt')
        obj.num_docs = len(obj.collection)
        obj.build()
        return obj

    # creat the matrix
    def build(self) -> None:
        incidence = dict()

        for doc_num, file_path in enumerate(self.collection):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                terms = nltk.word_tokenize(content)

            terms = set(normalize_list(terms))

            for term in terms:
                if term not in incidence:
                    incidence[term] = np.zeros(self.num_docs, dtype=np.int8)  # Add a row of zeros when a new term occurred

                incidence[term][doc_num] = 1

        self.matrix = pd.DataFrame.from_dict(incidence, orient='index', columns=get_files_names(self.collection))
        self.matrix.sort_index(inplace=True)

    # search in the matrix by applying the same preprocessing that used when building on the query
    # return list of documents which term was observed into it
    def search(self, query: str) -> list[str]:
        query = query.replace('AND', '&') \
            .replace('OR', '|').replace('NOT', '~').replace(' ', '')

        query_list = operator_split(query)

        postfix_query = infix_to_postfix(query_list)
        result = self.__solve(postfix_query)
        return self.matrix.columns[result == 1].tolist()

    # apply bitwise operations based on the desired query
    def __solve(self, postfix_query: list[str]) -> pd.Series:
        solve_stack = []

        for token in postfix_query:
            if token not in OPERATIONS:
                token = normalize(token)
                solve_stack.append(self.get(token))
                continue

            if token == '~':
                solve_stack[-1] = np.logical_not(solve_stack[-1])
                continue

            right = solve_stack.pop()
            left = solve_stack.pop()

            if token == '&':
                solve_stack.append(np.logical_and(left, right))
            elif token == '|':
                solve_stack.append(np.logical_or(left, right))

        if len(solve_stack) == 1:
            return solve_stack[0]

        raise Exception('Invalid query')

    # get term vector or vector of zeros if it does not exist in the matrix
    def get(self, term) -> np.ndarray:
        if term in self.matrix.index:
            return self.matrix.loc[term].values

        return np.zeros(self.num_docs, dtype=np.int8)

    def save(self, file_path: str) -> None:
        self.matrix.to_csv(file_path)

    @classmethod
    def load(cls, file_path: str):
        obj = cls()
        obj.matrix = pd.read_csv(file_path)
        obj.matrix.set_index(obj.matrix.iloc[:, 0].values, inplace=True)
        obj.matrix.drop(columns='Unnamed: 0', inplace=True)
        obj.num_docs = obj.matrix.shape[1]
        obj.collection = obj.matrix.columns
        return obj
