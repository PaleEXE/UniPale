import os

import nltk

# some constants
OPERATIONS = ['AND', 'OR', 'NOT']

PRECEDENCE = {
    'NOT': 3,
    'AND': 2,
    'OR':  1,
}

STEMMER = nltk.SnowballStemmer("english")


# small function to enhance readability
def precedence(op: int) -> int:
    return PRECEDENCE.get(op, -1)


# function that extracts file name from its path
# eg: C:\uni\mohammad.txt -> mohammad
def get_files_names(paths: list[str]) -> list[str]:
    return [os.path.basename(path)[:-4] for path in paths]


# create a postfix equation that makes it easier to deal with operations
# eg: red AND blue -> red blue AND
def infix_to_postfix(query_list: list[str]) -> list[str]:
    output = []
    operators = []

    for word in query_list:
        if word not in OPERATIONS and word.isalnum():
            output.append(word)

        elif word in OPERATIONS:
            while operators and precedence(operators[-1]) >= precedence(word):
                output.append(operators.pop())
            operators.append(word)

        elif word == '(':
            operators.append(word)

        elif word == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            if not operators:
                raise ValueError("Unbalanced parentheses")
            operators.pop()

        else:
            raise Exception(f"Invalid expression: {query_list}, Nuh uh")

    while operators:
        if operators[-1] == '(':
            raise ValueError("Unbalanced parentheses")
        output.append(operators.pop())

    return output


# stem and lowercase word
# eg: Eating -> eat
def normalize(word: str) -> str:
    return STEMMER.stem(word)


# stem and lowercase list of words using "normalize" method and filter numbers and punctuations
# eg: Eating, Government -> eat, govern
def normalize_list(words: list) -> list[str]:
    return [normalize(word) for word in words if word.isalpha()]
