import glob
import json

from utils import *


class InvertedIndex:
    def __init__(self):
        self.collection = []
        self.index = {}
        self.doc_names = []
        self.num_docs = 0

    @classmethod
    def from_folder(cls, folder_path: str):
        obj = cls()
        obj.collection = glob.glob(folder_path + '*.txt')
        obj.doc_names = get_files_names(obj.collection)
        obj.num_docs = len(obj.doc_names)
        obj.build()
        return obj

    def build(self) -> None:
        for doc_num, file_path in enumerate(self.collection):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                terms = nltk.word_tokenize(content)

            terms = normalize_list(terms)

            for term in terms:
                if term not in self.index:
                    self.index[term] = [doc_num]

                if self.index[term][-1] != doc_num:
                    self.index[term].append(doc_num)

        print(self.index['girl'])

    @staticmethod
    def intersection(list1: list, list2: list) -> list:
        result = []
        p1 = p2 = 0
        while p1 < len(list1) and p2 < len(list2):
            if list1[p1] < list2[p2]:
                p1 += 1
            elif list1[p1] > list2[p2]:
                p2 += 1
            else:
                result.append(list1[p1])
                p1 += 1
                p2 += 1

        return result

    @staticmethod
    def union(list1: list, list2: list) -> list:
        result = []
        p1 = p2 = 0

        while p1 < len(list1) and p2 < len(list2):
            if list1[p1] < list2[p2]:
                result.append(list1[p1])
                p1 += 1
            elif list1[p1] > list2[p2]:
                result.append(list2[p2])
                p2 += 1
            else:
                result.append(list1[p1])
                p1 += 1
                p2 += 1

        for i in range(p1, len(list1)):
            result.append(list1[i])

        for i in range(p2, len(list2)):
            result.append(list2[i])

        return result

    @staticmethod
    def complementary(list1: list, end_point: int) -> list:
        if not list1:
            return list(range(end_point))

        result = []
        p1 = 0
        for i in range(end_point):
            if i != list1[p1]:
                result.append(i)
                continue

            p1 += 1 if p1 < len(list1) -1 else 0

        return result

    def search(self, query: str) -> list[str]:
        query = query.replace('AND', '&') \
            .replace('OR', '|').replace('NOT', '~').replace(' ', '')

        query_list = operator_split(query)

        postfix_query = infix_to_postfix(query_list)
        result = self.__solve(postfix_query)
        return [self.doc_names[i] for i in result]

    def __solve(self, postfix_query: list[str]) -> list[int]:
        solve_stack = []

        for token in postfix_query:
            if token not in OPERATIONS:
                token = normalize(token)
                solve_stack.append(self.index.get(token, []))
                continue

            if token == '~':
                solve_stack[-1] = InvertedIndex.complementary(solve_stack[-1], self.num_docs)
                continue

            right = solve_stack.pop()
            left = solve_stack.pop()

            if token == '&':
                solve_stack.append(InvertedIndex.intersection(left, right))
            elif token == '|':
                solve_stack.append(InvertedIndex.union(left, right))

        if len(solve_stack) == 1:
            return solve_stack[0]

        raise Exception('Invalid query')

    def save(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(vars(self), file, ensure_ascii=False, indent=4)

    @classmethod
    def load(cls, path: str):
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        obj = cls()
        obj.collection = data['collection']
        obj.doc_names = data['doc_names']
        obj.num_docs = data['num_docs']
        obj.index = data['index']

        return obj


if __name__ == '__main__':
    # ivn = InvertedIndex.from_folder('../pale_ir/songs/')
    # print(ivn.search('love AND cars'))
    # print(ivn.search('Messi OR lady'))
    # print(ivn.search('Call AND NOT phone'))
    # ivn.save('data/inverted_index.json')
    ivn2 = InvertedIndex.load('data/inverted_index.json')
    # print(ivn2.search('Call'))
    print(ivn2.search('love AND NOT(cars OR girl OR man OR dog)'))


