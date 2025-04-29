import os
import glob
from matplotlib import pyplot as plt


def filter_to_numbers(text: str) -> int:
    result = []
    for char in text:
        if char.isdigit():
            result.append(char)
    return int(''.join(result))


sizes = []
for image in glob.glob("../../pale_image/images/decompression_mona_lisa/*.png"):
    sizes.append((
        filter_to_numbers(image),
        os.path.getsize(image) / 1024  # Convert bytes to KB
    ))

sizes = sorted(sizes, key=lambda x: x[0])

# Extract indices and sizes
indices = [x[0] for x in sizes]
sizes_in_kb = [x[1] for x in sizes]

# Create a stylish plot
plt.figure(figsize=(10, 6))
plt.plot(indices, sizes_in_kb, color="purple", marker='o', linestyle='-', markersize=5, linewidth=2)

# Add grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

# Customize labels and title
plt.xlabel("Image Index", fontsize=12, fontweight='bold', color='navy')
plt.ylabel("Size (KB)", fontsize=12, fontweight='bold', color='navy')
plt.title("PNG File Sizes (KB) - Mona Lisa", fontsize=14, fontweight='bold', color='darkgreen')

# Show plot with style improvements
plt.tight_layout()
plt.show()
