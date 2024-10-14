import itertools
from typing import List, Dict
from pprint import pprint

import numpy as np
import pandas as pd


def infix_to_postfix(expression: str) -> List[str]:
    precedence = {'~': 4, '&': 3, '^': 2.5, '|': 2, '-': 1, '=': 0}
    output: List[str] = []
    operators: List[str] = []

    def has_higher_precedence(op1: str, op2: str) -> bool:
        return (precedence[op1] > precedence[op2]) or (precedence[op1] == precedence[op2] and precedence[op1] < 4)

    for char in expression:
        if char.isalnum():
            output.append(char)
        elif char in precedence:
            while (operators and operators[-1] in precedence and
                   has_higher_precedence(operators[-1], char)):
                output.append(operators.pop())
            operators.append(char)
        elif char == '(':
            operators.append(char)
        elif char == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()

    while operators:
        output.append(operators.pop())

    return output


class PExp:
    def __init__(self, expression: str) -> None:
        self._expression: str = expression
        self._post_expression: List[str] = infix_to_postfix(expression)
        self._variable: List[str] = self._chars()
        self._key_elements: Dict[str, np.ndarray] = self._build_table()

    def _chars(self) -> List[str]:
        return list(filter(lambda x: x.isalnum(), self._expression))

    def _build_table(self) -> Dict[str, np.ndarray]:
        self._num_var: int = len(set(self._variable))
        rizz: Dict[str, np.ndarray] = {}
        for i, var in enumerate(sorted(list(set(self._variable))), start=1):
            j = 1 << i
            rizz.update(
                {
                    var: np.array(
                        list(
                            itertools
                            .chain
                            .from_iterable(
                                [[True] * (2 ** self._num_var // j) +
                                 [False] * (2 ** self._num_var // j)] * (j // 2)
                            )
                        )
                    )
                }
            )
        return rizz

    @property
    def expression(self) -> str:
        return self._expression

    @property
    def post_expression(self) -> List[str]:
        return self._post_expression

    @property
    def variable(self) -> List[str]:
        return self._variable

    @property
    def key_elements(self) -> Dict[str, List[bool]]:
        rizz = dict(zip(self._key_elements.keys(), [arr.tolist() for arr in self._key_elements.values()]))
        return rizz

    def solve(self) -> 'PExp':
        solve_stack: List[str] = []
        for elem in self._post_expression:
            if elem in self._variable:
                solve_stack.append(elem)
                continue

            right: str = solve_stack.pop()

            if elem == "~":
                value = ~self._key_elements[right]
                key: str = f"~{right}"
            else:
                lift: str = solve_stack.pop()
                key = f"{lift}{elem}{right}"

                if elem == "&":
                    value = self._key_elements[lift] & self._key_elements[right]
                elif elem == "|":
                    value = self._key_elements[lift] | self._key_elements[right]
                elif elem == "^":
                    value = self._key_elements[lift] ^ self._key_elements[right]
                elif elem == "=":
                    value = self._key_elements[lift] == self._key_elements[right]
                elif elem == "-":
                    value = ~self._key_elements[lift] | self._key_elements[right]
                else:
                    raise Exception(f"Invalid expression: {self._expression}, Nuh uh")

            self._key_elements.update({
                key: value
            })
            solve_stack.append(key)
            self._variable.append(key)

        if not solve_stack:
            raise Exception(f"Invalid expression: {self._expression}, Nuh uh")

        self._df = self._to_pandas()
        return self

    def show(self) -> 'PExp':
        pprint(self._key_elements)
        return self

    def show_table(self) -> 'PExp':
        print(self._df.to_markdown(), "\n")
        return self

    def final_answer(self) -> np.ndarray[bool]:
        return self._key_elements[self._variable[-1]]

    def _to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame(self._key_elements)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.astype("int8")

    def where(self, **kwargs) -> pd.DataFrame:
        con: np.ndarray = np.ones(2 ** self._num_var, dtype=bool)

        for k, v in kwargs.items():
            con &= (self._key_elements[k] == v)

        return self._df[con].astype("int8")

    def __eq__(self, other: 'PExp') -> bool:
        return all(self.final_answer() == other.final_answer())


if __name__ == "__main__":
    # exp0 = PExp("a&b-c|d").solve().show_table()
    # e0 = PExp("a").solve().show_table()
    # exp1 = PExp("~(a&b)|(c|d)").solve().show_table()
    # print(exp0.where(b=1, c=0).to_markdown(), '\n')
    print(PExp("a-b&c-k|p^x").solve().where(x=1, c=0, b=1, a=1, p=0, k=1).to_markdown())