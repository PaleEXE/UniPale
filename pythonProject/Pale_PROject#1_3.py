# Mohammad F Al-Hennawi half done project
import numpy as np
import json
import operator


def _form(obj):
    class_name: str = '_' + (str(obj.__class__).removeprefix("<class '__main__."))[:-2] + '__'
    return class_name


def save(obj, path):
    remv = _form(obj)
    m_all = operator.methodcaller('all')
    with open(path, 'w') as sj:
        all_res = []
        for i, element in enumerate(m_all(obj)):
            info = vars(element)
            res = {'ID': i}
            for k, v in info.items():
                if isinstance(v, np.ndarray):
                    continue
                res[k.removeprefix(remv)] = v
            all_res.append(res)
        json.dump(all_res, sj)


class Show:
    all_categories: list[str] = ["action", "comedy", "adventure", "tragedy", "romance"]
    all_shows_cat: np.array(np.array([float])) = np.array([])  # type: ignore
    all_shows_stars: np.array(np.array([float])) = np.array([])  # type: ignore
    all_shows_names: np.array(np.array([str])) = np.array([])
    sum_all: np.array(np.array([int])) = np.array([])
    all_shows: list = []

    def __init__(self, name: str, categories: dict, stars: float = 2.5, age: int = 18) -> None:
        self.__name = name
        self.__dict_cat = categories
        self.__categories = set_categories(categories)
        self.__stars = stars
        self.__age = age
        Show.all_shows.append(self)
        Show.all_shows_cat = np.append(Show.all_shows_cat, self.__categories).reshape(len(Show.all_shows), len(Show.all_categories))
        Show.all_shows_stars = np.append(Show.all_shows_stars, self.__stars)
        Show.all_shows_names = np.append(Show.all_shows_names, self.__name)
        Show.sum_all = np.append(Show.sum_all, np.sum(self.__categories))

    @property
    def stars(self) -> float:
        return self.__stars

    @stars.setter
    def stars(self, s: float) -> None:
        self.__stars = s

    def get_name(self) -> str:
        return self.__name

    def get_age(self) -> int:
        return self.__age

    def get_categories(self) -> np.array([float]):
        return self.__categories

    @classmethod
    def all(_):
        return Show.all_shows


class User:
    count: int = 0
    all_users = []

    def __init__(self, name: str, fov: dict, birth_year: int, gender: bool = True) -> None:
        self.__name = name
        self.__fov = set_categories(fov)
        self.__age = 2023 - birth_year
        self.__gender = gender
        self.__fov = fov
        User.all_users.append(self)
        User.count += 1

    def get_age(self) -> int:
        return self.__age

    def get_fov(self) -> np.array([float]):
        return self.__fov

    def get_pronouns(self) -> tuple[str]:
        if self.__gender:
            return "she", "her", "hers"
        return "he", "him", "his"

    def get_name(self) -> str:
        return self.__name

    @classmethod
    def all(_):
        return User.all_users


def set_categories(dec: dict) -> np.array([float]):
    """ Sort and arrange values by categories """
    tmp: np.array([float]) = np.array([0] * len(Show.all_categories), dtype=float)
    for ind, cat in enumerate(Show.all_categories):
        if dec.get(cat):
            tmp[ind] = dec.get(cat)
    return tmp


def all_recommendations(user: User) -> np.array([str]):
    """ return all recommended shows for a specific user ( Age classification is not working here :3 )"""
    u: np.array([float]) = user.get_fov()
    scores: float = Show.all_shows_cat.dot(u) / (np.count_nonzero(u))
    final_scores = scores * Show.all_shows_stars / 2.5 > Show.sum_all
    result = Show.all_shows_names[final_scores]
    return result


def recommendation(show: Show, user: User) -> tuple[bool, str]:
    """ return if specific show is recommended for specific user """
    if user.get_age() > show.get_age():
        u: np.array([float]) = user.get_fov()
        s: np.array([float]) = show.get_categories()
        score: float = s.dot(u) / (len(u) - np.count_nonzero(u))
        if score * show.stars / 5 > sum(s):
            return True, f"{show.get_name()} is recommend for {user.get_name()}"
        return False, f"{show.get_name()} score is low, is`t recommend for {user.get_name()}"
    return False, f"{user.get_name()}`s age is low for watching {show.get_name()}"


s1 = Show("JOJO`s bizarres adventure", {"action": 10, "comedy": 10, "tragedy": 9, "adventure": 10}, 5.0, 13)
s2 = Show("One piece", {"action": 5, "comedy": 1, "adventure": 8}, 4, 13)
s3 = Show("Your lie in aprile", {"romance": 10, "tragedy": 10}, 4.5)
s4 = Show("The Dark knight", {"action": 9, "tragedy": 7}, 5.0, 18)
s5 = Show("Dumb and Dumber", {"comedy": 10, "adventure": 4}, 3, 13)
s6 = Show("FM A BH", {"tragedy": 9, "comedy": 5, "action": 100}, 4)

u1 = User("Mohammad", {"comedy": 10, "romance": 9}, 2004, False)
u2 = User("Hamza", {"action": 7, "comedy": 6, "adventure": 10}, 2006, False)
u69 = User("Hamza", {"action": 10, "comedy": 1000, "adventure": 7.5, "romance": 69}, 2006, False)
u3 = User("Soso", {"tragedy": 7, "romance": 10}, 2000)
u4 = User("lolo",  {"action": 7, "comedy": 8}, 2004)
u5 = User("Joseph", {"action": 8.9, "romance": 10, "adventure": 5, "comedy": 10}, 1899, False)

# save(u5, 'User.json')
# save(s6, 'Show.json')
