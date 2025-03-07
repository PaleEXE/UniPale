from PIL import Image


def decode_rle_to_rgb_image(input_file, output_image, width, height):
    with open(input_file, 'r') as file:
        encoded_data = file.readlines()

    decoded_pixels = []
    for line in encoded_data:
        r, g, b, count = map(int, line.strip().split())
        decoded_pixels.extend([(r, g, b)] * count)

    image = Image.new('RGB', (width, height))
    image.putdata(decoded_pixels)

    image.save(output_image)


decode_rle_to_rgb_image('i.txt', 'o.png', 1024, 1024)


