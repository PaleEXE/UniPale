use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read, Write};
use serde::{Serialize, Deserialize};
use crate::document::Document;

#[derive(Serialize, Deserialize, Debug)]
pub struct InvertedIndex {
    pub documents_map: HashMap<usize, String>,
    pub words: HashMap<String, Vec<(usize, usize)>>,
}

impl InvertedIndex {
    pub fn new() -> Self {
        InvertedIndex {
            documents_map: HashMap::new(),
            words: HashMap::new(),
        }
    }

    pub fn add_document(&mut self, doc: &Document) {
        for (word, count) in doc.word_count() {
            self.words.entry(word).or_insert_with(Vec::new).push((doc.id, count));
        }
        self.documents_map.insert(doc.id, doc.title.clone());
    }

    pub fn display(&self) {
        for (word, occurrences) in &self.words {
            println!("{}: {:?}", word, occurrences);
        }
    }

    pub fn save(&self, path: &str) -> io::Result<()> {
        let json_data = serde_json::to_string_pretty(self)
            .map_err(|e| io::Error::new(io::ErrorKind::Other, format!("Serialization error: {}", e)))?;

        let mut file = File::create(path)?;
        file.write_all(json_data.as_bytes())?;

        println!("Index successfully saved to {}", path);
        Ok(())
    }

    pub fn load(path: &str) -> io::Result<Self> {
        let mut file = File::open(path)?;
        let mut json_data = String::new();
        file.read_to_string(&mut json_data)?;

        serde_json::from_str(&json_data)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, format!("Deserialization error: {}", e)))
            .map(|index| {
                println!("Index successfully loaded from {}", path);
                index
            })
    }

    pub fn search(&self, query: &str) -> Vec<(String, f64)> {
        let tokens = query.split_whitespace().map(|s| s.to_string()).collect::<Vec<String>>();
        let mut scores: HashMap<usize, f64> = HashMap::new();

        for token in tokens.iter() {
            if let Some(doc_list) = self.words.get(token) {
                let df = doc_list.len() as f64; // Document frequency
                let idf = (self.documents_map.len() as f64 / (df + 1.0)).ln(); // Compute IDF (log scale)

                for (doc_id, tf) in doc_list {
                    let tf_weight = *tf as f64; // Term frequency in document
                    let score = tf_weight * idf; // TF-IDF formula
                    *scores.entry(*doc_id).or_insert(0.0) += score;
                }
            }
        }

        // Convert doc_id to title and sort by score (descending)
        let mut results: Vec<(String, f64)> = scores
            .into_iter()
            .map(|(doc_id, score)| (self.documents_map.get(&doc_id).unwrap().clone(), score))
            .collect();

        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        results
    }
}
