use std::collections::HashMap;
use std::fs;
use serde::{Serialize, Deserialize};

#[derive(Eq, Hash, PartialEq, Debug, Serialize, Deserialize)]
pub struct Document {
    pub title: String,
    pub content: String,
    pub id: usize,
}

impl Document {
    pub fn new(path: &str, id: usize) -> Self {
        Document {
            title: path.to_string(),
            content: fs::read_to_string(path).unwrap(),
            id,
        }
    }

    pub fn word_count(&self) -> HashMap<String, usize> {
        let mut counts = HashMap::new();
        for word in self.doc_split() {
            *counts.entry(word).or_insert(0) += 1;
        }
        counts
    }

    pub fn doc_split(&self) -> Vec<String> {
        let lowercased = self.content
            .to_lowercase()
            .chars()
            .filter(|ch| !".!>(){}[]*-<>,?:\"'".contains(*ch))
            .collect::<String>();

        lowercased.split_ascii_whitespace().map(|s| s.to_string()).collect()
    }

    pub fn from_vec(docs: &[String]) -> Vec<Document> {
        docs.iter().enumerate().map(|(index, doc)| Document::new(doc, index)).collect()
    }
}
