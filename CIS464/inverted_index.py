import glob

from utils import *


class InvertedIndex:
    def __init__(self, collection_path: str):
        self.collection = glob.glob(collection_path + "*.txt")
        self.index = {}
        self.doc_names = get_files_names(self.collection)
        self.num_docs = len(self.collection)

    def build(self):
        for doc_num, file_path in enumerate(self.collection):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                terms = set(nltk.word_tokenize(content))

            terms = normalize_list(terms)

            for term in terms:
                if term not in self.index:
                    self.index[term] = []

                self.index[term].append(doc_num)

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
            if list1[p1] != list2[p2]:
                result.append(list1[p1])

            result.append(list2[p2])

            p2 += 1
            p1 += 1

        for i in range(p1, len(list1)):
            result.append(list1[i])

        for i in range(p2, len(list2)):
            result.append(list2[i])

        return result

    @staticmethod
    def complementary(list1: list, end_point: int) -> list:
        result = []
        p1 = 0
        for i in range(end_point):
            if i != list1[p1]:
                result.append(i)
                continue

            p1 += 1 if p1 < len(list1) - 1 else 0

        return result

    def search(self, query: str) -> list[str]:
        query_list = nltk.word_tokenize(query)
        postfix_query = infix_to_postfix(query_list)
        result = self.__solve(postfix_query)
        return [self.doc_names[i] for i in result]

    def __solve(self, postfix_query: list[str]) -> list[int]:
        solve_stack = []

        for token in postfix_query:
            if token not in OPERATIONS and token.isalnum():
                token = normalize(token)
                solve_stack.append(self.index.get(token, [-1]))
                continue

            if token == 'NOT':
                solve_stack[-1] = InvertedIndex.complementary(solve_stack[-1], self.num_docs)
                continue

            right = solve_stack.pop()
            left = solve_stack.pop()

            if token == 'AND':
                solve_stack.append(InvertedIndex.intersection(left, right))
            elif token == 'OR':
                solve_stack.append(InvertedIndex.union(left, right))

        if len(solve_stack) == 1:
            return solve_stack[0]

        raise Exception("Invalid query")


if __name__ == '__main__':
    ivn = InvertedIndex("../pale_ir/songs/")
    ivn.build()
    print(ivn.search("love AND cars"))
    print(ivn.search('Messi OR lady'))
    print(ivn.search('Call AND NOT phone'))
