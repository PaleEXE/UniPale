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

from inverted_index import InvertedIndex
from incidence_matrix import IncidenceMatrix

inc = IncidenceMatrix.load('data/incidence_matrix.csv')
inv = InvertedIndex.load('data/inverted_index.json')

assert inc.search('love AND NOT(cars OR girl OR man OR dog)') == inv.search('love AND NOT(cars OR girl OR man OR dog)')