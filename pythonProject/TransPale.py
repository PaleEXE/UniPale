from collections import Counter
import glob
import string
import multiprocessing
import json

import nltk
from icecream import ic


stemmer = nltk.stem.snowball.SnowballStemmer("english")


def get_word_count(path: str) -> dict[str: int]:
    with open(path) as file:
        return path, Counter(
            filter(
                lambda x: "'" not in x
                          and x not in string.punctuation
                          and x not in nltk.corpus.stopwords.words('english'),
                map(
                    stemmer.stem,
                    nltk.tokenize.word_tokenize(
                        file.read()
                    )
                )
            )
        )


def save(path: str, data: dict) -> None:
    with open(path, 'w') as j_file:
        json.dump(data, j_file, indent=4)


if __name__ == '__main__':

    glob_folder = 'Modern Talking'
    songs_list = glob.glob(f'{glob_folder}/*.txt')

    with multiprocessing.Pool() as pool:
        riz = pool.imap_unordered(get_word_count, songs_list)

        for ind, (name, count) in enumerate(riz):
            name = name.removeprefix('Modern Talking\\')[:-4]
            ic(name, count)
            out = {
                'ID': ind,
                'Name': name,
                'Words': dict(count)
            }
            save(f'{glob_folder} (Processed)\\{name}.json', out)
