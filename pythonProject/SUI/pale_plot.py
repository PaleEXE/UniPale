import os
import glob
from matplotlib import pyplot as plt


def filter_to_numbers(text: str) -> int:
    result = []
    for char in text:
        if char.isdigit():
            result.append(char)
    return int(''.join(result))


# Define the path to the original image
original_image_path = "../../pale_image/images/Mona_Lisa.png"
original_size_kb = os.path.getsize(original_image_path) / 1024  # Convert to KB

# Collect decompressed image sizes
sizes = []
for image in glob.glob("../../pale_image/images/decompression_mona_lisa/*.png"):
    sizes.append((
        filter_to_numbers(image),
        os.path.getsize(image) / 1024  # Convert bytes to KB
    ))

sizes = sorted(sizes, key=lambda x: x[0])
indices = [x[0] for x in sizes]
sizes_in_kb = [x[1] for x in sizes]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(indices, sizes_in_kb, color="plum", marker='o', linestyle='-', markersize=5, linewidth=2)

# Add horizontal line for original image size
plt.axhline(y=original_size_kb, color='goldenrod', linestyle='--', linewidth=2, label=f'Original Image ({original_size_kb:.1f} KB)')

# Decorations
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xlabel("Dissimilarity Margin in bits", fontsize=12, fontweight='bold', color='plum')
plt.ylabel("Size (KB)", fontsize=12, fontweight='bold', color='plum')
plt.title("PNG File Sizes (KB) - Mona Lisa", fontsize=14, fontweight='bold', color='plum')
plt.ylim(bottom=0)
plt.legend()
plt.tight_layout()
plt.show()
