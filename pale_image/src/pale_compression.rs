use image::{Rgb, RgbImage};
use std::fs::File;
use std::io::{Read, Write};
use zstd::stream::{Encoder, Decoder};

struct EncodedPixelsCompact {
    color: u16,
}

impl EncodedPixelsCompact {
    pub fn new(r: u8, g: u8, b: u8) -> Self {
        let rgb565 = ((r as u16 >> 3) << 11) | ((g as u16 >> 2) << 5) | (b as u16 >> 3);
        Self { color: rgb565 }
    }

    pub fn color_rgb(&self) -> (u8, u8, u8) {
        let rgb565 = self.color;
        let r = ((rgb565 >> 11) & 0x1F) << 3;
        let g = ((rgb565 >> 5) & 0x3F) << 2;
        let b = (rgb565 & 0x1F) << 3;
        (r as u8, g as u8, b as u8)
    }
}

pub(crate) struct PaleImage {
    pixels: Vec<Vec<(u16, EncodedPixelsCompact)>>,
    width: u32,
    height: u32,
}

impl PaleImage {
    pub fn compress(img: &RgbImage, dissimilarity_margin: i16) -> Self {
        let (width, height) = img.dimensions();
        let mut encoded_rows = Vec::new();

        for y in 0..height {
            let mut row_colors: Vec<(u16, EncodedPixelsCompact)> = Vec::new();
            let mut x = 0;
            while x < width {
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
                    if Self::is_similar(&first_pixel, &current_pixel, dissimilarity_margin) {
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

                row_colors.push((count as u16, EncodedPixelsCompact::new(avg_r, avg_g, avg_b)));
                x += 1;
            }
            encoded_rows.push(row_colors);
        }

        Self {
            pixels: encoded_rows,
            width,
            height,
        }
    }

    pub fn lossless_compress(img: &RgbImage) -> Self {
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
        for (y, row) in self.pixels.iter().enumerate() {
            let mut x = 0;
            for (len, color) in row {
                let (r, g, b) = color.color_rgb();
                for _ in 0..*len {
                    img.put_pixel(x, y as u32, Rgb([r, g, b]));
                    x += 1;
                }
            }
        }
        img
    }

    pub fn from_path(path: &str) -> Result<RgbImage, Box<dyn std::error::Error>> {
        let img_bytes = std::fs::read(path)?;
        let img = image::load_from_memory(&img_bytes)?.to_rgb8();
        Ok(img)
    }

    pub fn save(&self, path: &str) -> std::io::Result<()> {
        let file = File::create(path)?;
        let mut encoder = Encoder::new(file, 22)?; // max compression

        encoder.write_all(&self.width.to_le_bytes())?;
        encoder.write_all(&self.height.to_le_bytes())?;

        for row in &self.pixels {
            encoder.write_all(&(row.len() as u32).to_le_bytes())?;
            for (count, color) in row {
                encoder.write_all(&count.to_le_bytes())?;
                encoder.write_all(&color.color.to_le_bytes())?;
            }
        }

        encoder.finish()?;
        Ok(())
    }

    pub fn load(path: &str) -> std::io::Result<Self> {
        let file = File::open(path)?;
        let mut decoder = Decoder::new(file)?;
        let mut buf = Vec::new();
        decoder.read_to_end(&mut buf)?;

        let mut cursor = 0;

        let width = u32::from_le_bytes(buf[cursor..cursor + 4].try_into().unwrap());
        cursor += 4;
        let height = u32::from_le_bytes(buf[cursor..cursor + 4].try_into().unwrap());
        cursor += 4;

        let mut pixels = Vec::new();
        for _ in 0..height {
            let row_len = u32::from_le_bytes(buf[cursor..cursor + 4].try_into().unwrap()) as usize;
            cursor += 4;

            let mut row = Vec::new();
            for _ in 0..row_len {
                let count = u16::from_le_bytes(buf[cursor..cursor + 2].try_into().unwrap());
                cursor += 2;
                let color = u16::from_le_bytes(buf[cursor..cursor + 2].try_into().unwrap());
                cursor += 2;
                row.push((count, EncodedPixelsCompact { color }));
            }

            pixels.push(row);
        }

        Ok(Self { pixels, width, height })
    }
}
