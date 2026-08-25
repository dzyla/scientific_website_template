import mrcfile
import numpy as np
import matplotlib.pyplot as plt

file_in = './cryosparc_P8_J67_050_class_averages.mrc'

with mrcfile.open(file_in) as mrc:
    data = mrc.data

print(f"Data shape: {data.shape}")

# generate a 2D image grid
def generate_2d_grid(data, grid_size=(5, 5), img_size=(64, 64), spacing=5):
    rows, cols = grid_size
    img_h, img_w = img_size
    grid_h = rows * img_h + (rows - 1) * spacing
    grid_w = cols * img_w + (cols - 1) * spacing

    grid_image = np.ones((grid_h, grid_w)) * np.min(data)

    for i in range(rows):
        for j in range(cols):
            idx = i * cols + j
            if idx >= data.shape[0]:
                break
            img = data[idx]
            img_resized = np.resize(img, img_size)
            y_start = i * (img_h + spacing)
            x_start = j * (img_w + spacing)
            grid_image[y_start:y_start+img_h, x_start:x_start+img_w] = img_resized

    # clip contrast
    p1, p99 = np.percentile(grid_image, (1, 100))
    grid_image = np.clip(grid_image, p1, p99)
    grid_image = (grid_image - p1) / (p99 - p1)
    grid_image = (grid_image * 255).astype(np.uint8)

    return grid_image

grid_image = generate_2d_grid(data, grid_size=(6, 8), img_size=(64, 64), spacing=0)

plt.figure(dpi=150)
plt.imshow(grid_image, cmap='gray', interpolation='nearest', aspect='auto')
plt.axis('off')
# make it 4 by 3 and remove white rim
plt.subplots_adjust(left=0.0, right=1.0, top=1, bottom=0)
plt.tight_layout()

plt.savefig('assets/images/2d_grid.png', dpi=150, bbox_inches='tight', pad_inches=0)
plt.show()