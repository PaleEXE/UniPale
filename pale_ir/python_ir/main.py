from document import Document
from inverted_index import InvertedIndex


# inverted_index = InvertedIndex()
# inverted_index.from_folder('..\\songs')
# inverted_index.save_to_json('inverted_index.json')

output_file = open('result.txt', 'w')

loaded_index = InvertedIndex.load_from_json('inverted_index.json')

rizz = loaded_index.search('love')

print("Query for 'love':", file=output_file)
loaded_index.print_scores(rizz, file=output_file)

new_doc0 = Document("Don\'t Call Tonight.txt", 117)
new_doc1 = Document('Let It Happen.txt', 17)

loaded_index.add_document(new_doc0)
loaded_index.add_document(new_doc1)

new_rizz = loaded_index.search('happen')

print("Query for 'let':", file=output_file)
loaded_index.print_scores(new_rizz, file=output_file)
