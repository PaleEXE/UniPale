# import glob
#
# for filename in glob.glob('*.py'):
#     if 'main' in filename:
#         continue
#
#     with open(filename, 'r+') as f:
#         content = f.read()
#         content = content.replace('"', "'")
#
#         f.seek(0)
#         f.write(content)
#         f.truncate()

if __name__ == '__main__':
    from search_engines.utils import *
    from search_engines.inverted_index import InvertedIndex
    from search_engines.incidence_matrix import IncidenceMatrix
    from search_engines.count_matrix import CountMatrix
    from search_engines.ranked_index import RankedIndex

    inc = IncidenceMatrix.from_folder('songs/')
    inv = InvertedIndex.from_folder('songs/')
    cot = CountMatrix.from_folder('songs/')
    rnk = RankedIndex.from_folder('songs/')

    query = 'six feet below the ground'
    result = rnk.search(query)

    print(query + '\n\n')
    print_scors(result)

    inc.save('data/incidence_matrix.csv')
    cot.save('data/count_matrix.csv')
    inv.save('data/incidence_matrix.json')
    rnk.save('data/ranked_index.json')

