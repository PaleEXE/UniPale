mod pale_compression;

use rayon::prelude::*;

fn main() {
    let img = pale_compression::PaleImage::from_path("images/Germany-Flag.png").unwrap();
    let pale_img = pale_compression::PaleImage::lossless_compress(&img);

    pale_img.save("images/compression_germany.bin").unwrap();

    let new_img = pale_compression::PaleImage::load("images/compression_germany.bin")
        .unwrap()
        .decompress();

    new_img.save("images/new_germany.png").unwrap();

    let pale_img2 = pale_compression::PaleImage::compress(&img, 16);

    pale_img2.save("images/compression_germany2.bin").unwrap();
    pale_img2.decompress().save("images/new_germany2.png").unwrap();

    let mona_lisa = pale_compression::PaleImage::from_path("images/Mona_Lisa.png")
        .unwrap();

    let margins = (0..=128)
        .step_by(8)
        .collect::<Vec<i16>>();

    margins
        .clone()
        .into_par_iter()
        .for_each(|margin| {
            println!("{}", margin);
            let pale_lisa = pale_compression::PaleImage::compress(&mona_lisa, margin);

            pale_lisa
                .save(&format!("images/compression_mona_lisa/{margin}.bin"))
                .unwrap();

            let new_lisa = pale_lisa.decompress();

            new_lisa
                .save(&format!("images/decompression_mona_lisa/{margin}.png"))
                .unwrap();
        });
}
