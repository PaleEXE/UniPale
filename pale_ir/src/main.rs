mod document;
mod inverted_index;
mod utils;

use std::time::Instant;

fn main() {
    let start = Instant::now();
    let mut index = inverted_index::InvertedIndex::new();
    for doc in document::Document::from_vec(&utils::read_dir("songs").unwrap()) {
        index.add_document(&doc)
    }
    index.save("inverted_index.json").unwrap();

    let loaded_index = inverted_index::InvertedIndex::load("inverted_index.json")
        .unwrap();

    for res in loaded_index.search("sea") {
        println!("Song: {}\nScore: {}\n", res.0, res.1);
    }
    println!("Time it took: {:?}", start.elapsed())
}
