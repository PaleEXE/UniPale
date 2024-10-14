import json
import glob

from icecream import ic
import pymongo


def read(path: str):
    with open(path) as j_file:
        data = json.load(j_file)
    return data


def upload(db, folder: str, data: list[dict]) -> None:
    directory = db[folder]
    directory.insert_one(
        ic(data)
    )


if __name__ == '__main__':
    client = pymongo.MongoClient()
    db = client.SONGS

    glob_folder = r'Modern Talking (Processed)'
    songs_list = glob.glob(f'{glob_folder}/*.json')
    db.drop_collection('songs')
    for song in songs_list:
        data = read(song)
        direct = ''.join(list(filter(lambda x: str.isalpha(x) or (x == '_'), list(data['Name'].replace(' ', '_')))))
        print(direct)
        upload(db['Modern_Talking'], direct, data)

