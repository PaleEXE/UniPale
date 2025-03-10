from collections import Counter
import nltk
from typing import Dict, List


stemmer = nltk.stem.PorterStemmer()


class Document:
    def __init__(self, path: str, _id: int) -> None:
        self.path: str = path
        self._id: int = _id

        with open(path, "r", encoding="utf-8") as file:
            self.content: str = file.read()

        self.words: List[str] = nltk.word_tokenize(self.content.lower())

        # Count words and stems
        self.word_counter: Dict[str, int] = Counter(filter(str.isalnum, self.words))
        self.stem_counter: Dict[str, int] = self.compute_stem_counter(self.words)

    def get_id(self) -> int:
        return self._id

    @staticmethod
    def compute_stem_counter(words: List[str]) -> Counter[str, int]:
        stem_words = map(stemmer.stem, filter(str.isalnum, words))
        return Counter(stem_words)


if __name__ == "__main__":
    doc = Document("../songs/Starboy.txt", 8)
    print(doc.words)
    print(doc.word_counter)
    print(doc.stem_counter)
