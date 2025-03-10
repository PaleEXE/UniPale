use std::fs;
use std::io;

#[allow(dead_code)]
pub fn read_dir(path: &str) -> io::Result<Vec<String>> {
    let mut files = Vec::new();
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let file_name = entry.file_name().into_string().unwrap_or_else(|_| "<Invalid UTF-8>".to_string());
        files.push(format!("{}/{}", path, file_name));
    }
    Ok(files)
}
