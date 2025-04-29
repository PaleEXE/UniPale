use image::{Rgb, RgbImage};
use zstd::stream::{Decoder, Encoder};
use std::fs::File;
use std::io::{Read, Write};
use serde::Serialize;

struct EncodedPixelsCompact {
    row_start: u32,  // Pack row (16 bits) + start (16 bits)
    end_color: u32,  // Pack end (16 bits) + RGB (5-6-5 bits)
}

impl EncodedPixelsCompact {
    pub fn new(row: u16, start_x: u16, end_x: u16, r: u8, g: u8, b: u8) -> Self {
        let row_start = ((row as u32) << 16) | (start_x as u32);
        let rgb565 = ((r as u16 >> 3) << 11) | ((g as u16 >> 2) << 5) | (b as u16 >> 3);
        let end_color = ((end_x as u32) << 16) | rgb565 as u32;
        Self { row_start, end_color }
    }

    pub fn to_bytes(&self) -> [u8; 8] {
        let mut bytes = [0u8; 8];
        bytes[..4].copy_from_slice(&self.row_start.to_le_bytes());
        bytes[4..].copy_from_slice(&self.end_color.to_le_bytes());
        bytes
    }

    pub fn from_bytes(bytes: &[u8]) -> Self {
        let row_start = u32::from_le_bytes(bytes[0..4].try_into().unwrap());
        let end_color = u32::from_le_bytes(bytes[4..8].try_into().unwrap());
        Self { row_start, end_color }
    }

    pub fn row(&self) -> u16 {
        (self.row_start >> 16) as u16
    }

    pub fn start(&self) -> u16 {
        self.row_start as u16
    }

    pub fn end(&self) -> u16 {
        (self.end_color >> 16) as u16
    }

    pub fn color_rgb(&self) -> (u8, u8, u8) {
        let rgb565 = self.end_color as u16;
        let r = ((rgb565 >> 11) & 0x1F) << 3;
        let g = ((rgb565 >> 5) & 0x3F) << 2;
        let b = (rgb565 & 0x1F) << 3;
        (r as u8, g as u8, b as u8)
    }
}

pub struct PaleImage {
    pub encoded_bytes: Vec<u8>,
    pub width: u32,
    pub height: u32,
}

impl PaleImage {
    pub fn compress(img: &RgbImage, dissimilarity_margin: i16) -> Self {
        let (width, height) = img.dimensions();
        let mut encoded_bytes = Vec::new();

        for y in 0..height {
            let mut x = 0;
            while x < width {
                let start_x = x;
                let mut sum_r = 0u32;
                let mut sum_g = 0u32;
                let mut sum_b = 0u32;
                let mut count = 0u32;

                let first_pixel = img.get_pixel(x, y).0;
                sum_r += first_pixel[0] as u32;
                sum_g += first_pixel[1] as u32;
                sum_b += first_pixel[2] as u32;
                count += 1;

                while x + 1 < width {
                    let current_pixel = img.get_pixel(x + 1, y).0;
                    if PaleImage::is_similar(&first_pixel, &current_pixel, dissimilarity_margin) {
                        sum_r += current_pixel[0] as u32;
                        sum_g += current_pixel[1] as u32;
                        sum_b += current_pixel[2] as u32;
                        count += 1;
                        x += 1;
                    } else {
                        break;
                    }
                }

                let avg_r = (sum_r / count) as u8;
                let avg_g = (sum_g / count) as u8;
                let avg_b = (sum_b / count) as u8;

                let packed = EncodedPixelsCompact::new(
                    y as u16,
                    start_x as u16,
                    x as u16,
                    avg_r,
                    avg_g,
                    avg_b,
                );
                encoded_bytes.extend_from_slice(&packed.to_bytes());
                x += 1;
            }
        }

        PaleImage {
            encoded_bytes,
            width,
            height,
        }
    }


    pub fn from_path(path: &str) -> Result<RgbImage, Box<dyn std::error::Error>> {
        let img_bytes = std::fs::read(path)?;
        let img = image::load_from_memory(&img_bytes)?.to_rgb8();
        Ok(img)
    }

    pub fn lossless_compression(img: &RgbImage) -> Self {
        PaleImage::compress(img, 0)
    }

    fn is_similar(a: &[u8; 3], b: &[u8; 3], margin: i16) -> bool {
        let dr = (a[0] as i16 - b[0] as i16).abs();
        let dg = (a[1] as i16 - b[1] as i16).abs();
        let db = (a[2] as i16 - b[2] as i16).abs();
        dr + dg + db <= margin
    }

    pub fn decompress(&self) -> RgbImage {
        let mut img = RgbImage::new(self.width, self.height);

        for chunk in self.encoded_bytes.chunks(8) {
            let enc = EncodedPixelsCompact::from_bytes(chunk);
            let (r, g, b) = enc.color_rgb();
            for x in enc.start()..=enc.end() {
                img.put_pixel(x as u32, enc.row() as u32, Rgb([r, g, b]));
            }
        }

        img
    }

    pub fn save(&self, path: &str) -> std::io::Result<()> {
     let file = File::create(path)?;
        let mut encoder = Encoder::new(file, 22)?; // ultra compression

        // Serialize width, height, then the encoded bytes
        encoder.write_all(&self.width.to_le_bytes())?;
        encoder.write_all(&self.height.to_le_bytes())?;
        encoder.write_all(&(self.encoded_bytes.len() as u32).to_le_bytes())?;
        encoder.write_all(&self.encoded_bytes)?;
        encoder.finish()?;
        Ok(())
    }

    pub fn load(path: &str) -> std::io::Result<Self> {
        let file = File::open(path).unwrap();
        let mut decoder = Decoder::new(file).unwrap();
        let mut buf = Vec::new();
        decoder.read_to_end(&mut buf).unwrap();

        let width = u32::from_le_bytes(buf[0..4].try_into().unwrap());
        let height = u32::from_le_bytes(buf[4..8].try_into().unwrap());
        let len = u32::from_le_bytes(buf[8..12].try_into().unwrap()) as usize;

        let encoded_bytes = buf[12..12 + len].to_vec();

        Ok(PaleImage { encoded_bytes, width, height })
    }
}


#[derive(Serialize)]
pub struct CompressionStats {
    dissimilarity_margin: i16,
    original_size: usize,
    binary_size: usize,
    decompressed_png_size: usize,
    compression_ratio: f32,
}

impl CompressionStats {
    pub(crate) fn new(
        dissimilarity_margin: i16,
        original_size: usize,
        binary_size: usize,
        decompressed_png_size: usize,
    ) -> Self {
        CompressionStats {
            dissimilarity_margin,
            original_size,
            binary_size,
            decompressed_png_size,
            compression_ratio: original_size as f32 / decompressed_png_size as f32,
        }
    }

    pub(crate) fn save_stats(stats: &Vec<CompressionStats>, path: &str) {
        let json = serde_json::to_string_pretty(stats).unwrap();
        std::fs::write(path, json).unwrap();
    }
}
