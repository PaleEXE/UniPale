import os

import nltk


# some constants
OPERATIONS = ['&', '|', '~']

PRECEDENCE = {
    '~': 3,
    '&': 2,
    '|': 1,
}

STEMMER = nltk.SnowballStemmer('english')


# small function to enhance readability
def precedence(op: int) -> int:
    return PRECEDENCE.get(op, -1)


# function that extracts file name from its path
# eg: C:\uni\mohammad.txt -> mohammad
def get_files_names(paths: list[str]) -> list[str]:
    return [os.path.basename(path)[:-4] for path in paths]


# a split function that keeps the separators
# eg: A&B|M -> [A, &, B, |, M]
def operator_split(text: str) -> list[str]:
    result = []
    start = 0

    for i, char in enumerate(text):
        if char in OPERATIONS:
            if i != start:
                result.append(text[start:i])

            start = i + 1
            result.append(char)

        if char == '(':
            result.append(char)
            start = i + 1

        if char == ')':
            result.append(text[start:i])
            start = i + 1
            result.append(char)

    if i + 1 != start:
        result.append(text[start:])

    return result

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
                raise ValueError('Unbalanced parentheses')
            operators.pop()

        else:
            raise Exception(f'Invalid expression: {query_list}, Nuh uh')

    while operators:
        if operators[-1] == '(':
            raise ValueError('Unbalanced parentheses')
        output.append(operators.pop())

    return output


# stem and lowercase word
# eg: Eating -> eat
def normalize(word: str) -> str:
    return STEMMER.stem(word)


# stem and lowercase list of words using 'normalize' method and filter numbers and punctuations
# eg: Eating, Government -> eat, govern
def normalize_list(words: list) -> list[str]:
    return [normalize(word) for word in words if word.isalpha()]


# small formated print for prettier output
def print_scors(scores: list) -> None:
    print(f'{"Documents:":<30}Scores')
    for score in scores:
        print(f' {score[0]:<30}{score[1]:.3f}')
