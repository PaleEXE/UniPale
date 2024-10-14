import re
import json
import operator
import numpy as np


class Show:
    """
    Represents a TV show, including its name, categories, stars, and release year.
    """
    all_categories = ["action", "comedy", "adventure", "tragedy", "romance"]
    all_shows_cat_list = []
    all_shows_stars_list = []
    all_shows_names_list = []
    sum_all_list = []
    all_shows = []

    def __init__(self, name, categories, stars=2.5, release_year=2000):
        self.__name = name
        self.__categories = self.set_categories(categories)
        self.__stars = stars
        self.__release_year = release_year

        # Add show to class-level collections (lists)
        Show.all_shows.append(self)
        Show.all_shows_cat_list.append(self.__categories)
        Show.all_shows_stars_list.append(self.__stars)
        Show.all_shows_names_list.append(self.__name)
        Show.sum_all_list.append(np.sum(self.__categories))

    @property
    def stars(self):
        return self.__stars

    @stars.setter
    def stars(self, value):
        self.__stars = value

    def get_name(self):
        return self.__name

    def get_release_year(self):
        return self.__release_year

    def get_categories(self):
        return self.__categories

    @classmethod
    def all(cls):
        return cls.all_shows

    @staticmethod
    def set_categories(categories):
        """Map category weights to a predefined list of categories."""
        category_array = np.zeros(len(Show.all_categories), dtype=float)
        for index, category in enumerate(Show.all_categories):
            category_array[index] = categories.get(category, 0)
        return category_array

    @staticmethod
    def np_array_to_dict(arr):
        return {
            Show.all_categories[i]: val for i, val in enumerate(arr) if val
        }

    @classmethod
    def convert_to_numpy(cls):
        """
        Convert class-level lists to Numpy arrays for efficient computation.
        """
        cls.all_shows_cat = np.array(cls.all_shows_cat_list, dtype=float)
        cls.all_shows_stars = np.array(cls.all_shows_stars_list, dtype=float)
        cls.all_shows_names = np.array(cls.all_shows_names_list, dtype=str)
        cls.sum_all = np.array(cls.sum_all_list, dtype=int)


class User:
    """
    Represents a user, including their name, preferences, birth year, and gender.
    """
    all_users = []

    def __init__(self, name, preferences, birth_year, gender=True):
        self.__name = name
        self.__preferences = Show.set_categories(preferences)
        self.__birth_year = birth_year
        self.__gender = gender

        # Add user to class-level collections
        User.all_users.append(self)

    def age(self):
        """Calculate the user's age based on the current year."""
        current_year = 2024  # Assuming the current year is 2024
        return current_year - self.__birth_year

    def get_preferences(self):
        return self.__preferences

    def get_pronouns(self):
        return ("she", "her", "hers") if self.__gender else ("he", "him", "his")

    def get_name(self):
        return self.__name

    @classmethod
    def all(cls):
        return cls.all_users


def all_recommendations(user):
    """
    Generate and return a sorted list of recommended shows for a specific user based on their preferences.

    Args:
        user (User): The user object for whom recommendations are generated.

    Returns:
        list[tuple[str, float]]: A list of tuples where each tuple contains the show name and its recommendation score,
                                 sorted by score in descending order, with native Python types.
    """
    # Retrieve user preferences as a numpy array
    user_preferences = user.get_preferences()

    # Calculate recommendation scores using dot product of user preferences and show categories
    if np.count_nonzero(user_preferences) > 0:
        scores = Show.all_shows_cat.dot(user_preferences) / np.count_nonzero(user_preferences)
    else:
        scores = np.zeros(len(Show.all_shows_cat))  # Handle case where user preferences are all zeroes

    # Combine show names with their respective scores
    recommendations = list(zip(Show.all_shows_names, scores))

    # Sort recommendations based on score in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # Convert numpy types to native Python types (str and float)
    recommendations = [(str(show_name), round(float(score), 2)) for show_name, score in recommendations]

    return recommendations


def recommendation(show, user):
    """
    Determine if a specific show is recommended for a specific user.

    Args:
        show: The show to check.
        user: The user for whom the recommendation is being checked.

    Returns:
        A tuple containing a boolean recommendation and a message.
    """
    if user.age() < (2024 - show.get_release_year()):
        return False, f"{user.get_name()}'s age is too low for watching {show.get_name()}"

    user_prefs = user.get_preferences()
    show_categories = show.get_categories()
    score = show_categories.dot(user_prefs) / np.count_nonzero(user_prefs)
    if (score * show.stars / 5) > np.sum(show_categories):
        return True, f"{show.get_name()} is recommended for {user.get_name()}"

    return False, f"{show.get_name()} has a low score, not recommended for {user.get_name()}"


def read(path, obj_type):
    """
    Load JSON data from a file and convert it into objects of the specified type.

    Args:
        path: The file path from which to read the JSON data.
        obj_type: The class type (User or Show) to convert the data into.

    Returns:
        A list of objects of the specified type.
    """
    with open(path, 'r') as file:
        data = json.load(file)

    objects = []
    for item in data:
        if obj_type == User:
            user = User(
                name=item.get('name'),
                preferences=item.get('preferences', {}),
                birth_year=item.get('birth_year'),
                gender=item.get('gender', True)
            )
            objects.append(user)
        elif obj_type == Show:
            show = Show(
                name=item.get('name'),
                categories=item.get('categories', {}),
                stars=item.get('stars', 2.5),
                release_year=item.get('release_year', 2000)
            )
            objects.append(show)

    return objects


def _get_class_name(obj):
    """
    Generate a class name string using regular expressions to extract the class name.

    Args:
        obj: An instance of a class.

    Returns:
        A formatted string representing the class name.
    """
    class_name = re.sub(r"<class '__main__\.(\w+)'>", r'_\1__', str(obj.__class__))
    return class_name


def save(obj, path):
    """
    Save the attributes of an object to a JSON file.

    Args:
        obj: The object to save.
        path: The file path to save the object data.
    """
    class_prefix = _get_class_name(obj)
    all_objects = operator.methodcaller('all')(obj)

    with open(path, 'w') as file:
        data_to_save = []
        for index, element in enumerate(all_objects):
            info = vars(element)
            data = {'ID': index}

            for key, value in info.items():
                if not isinstance(value, np.ndarray):
                    data[key.removeprefix(class_prefix)] = value
                else:
                    data['categories'] = Show.np_array_to_dict(value)

            data_to_save.append(data)

        json.dump(data_to_save, file, indent=4)


# Example usage
s1 = Show("JOJO's Bizarre Adventure", {"action": 10, "comedy": 10, "tragedy": 9, "adventure": 10}, 5.0, 2012)
s2 = Show("One Piece", {"action": 5, "comedy": 1, "adventure": 8}, 4, 1999)
s3 = Show("Your Lie in April", {"romance": 10, "tragedy": 10}, 4.5, 2014)
s4 = Show("The Dark Knight", {"action": 9, "tragedy": 7}, 5.0, 2008)
s5 = Show("Dumb and Dumber", {"comedy": 10, "adventure": 4}, 3, 1994)
s6 = Show("FM A BH", {"tragedy": 9, "comedy": 5, "action": 100}, 4, 2023)
Show.convert_to_numpy()
u1 = User("Mohammad", {"comedy": 10, "romance": 9}, 2004, False)
u2 = User("Hamza", {"action": 7, "comedy": 6, "adventure": 10}, 2006, False)
u3 = User("Soso", {"tragedy": 7, "romance": 10}, 2000)

print(all_recommendations(u1))
print(all_recommendations(u2))
print(all_recommendations(u3))

save(u1, 'User.json')
save(s1, 'Show.json')
