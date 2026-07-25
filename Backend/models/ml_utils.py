import math
import struct
from pathlib import Path

def load_bmp_image(file_path: Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    """Load a 24-bit uncompressed BMP image in pure Python."""
    with open(file_path, "rb") as f:
        data = f.read()
    
    magic, file_size, _, _, offset = struct.unpack("<2sIHHI", data[:14])
    dib_size, width, height, planes, bpp = struct.unpack("<IiiHH", data[14:30])
    
    assert magic == b"BM" and bpp == 24, f"Unsupported image format: {file_path}"
    
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    
    pixels = []
    # BMP stores rows bottom-to-top
    for y in range(height - 1, -1, -1):
        row_start = offset + y * (row_bytes + padding)
        row_pixels = []
        for x in range(width):
            px_idx = row_start + x * 3
            b = data[px_idx]
            g = data[px_idx + 1]
            r = data[px_idx + 2]
            row_pixels.append((r, g, b))
        pixels.extend(row_pixels)
        
    return width, height, pixels

def extract_features(pixels: list[tuple[int, int, int]], width: int = 224, height: int = 224) -> list[float]:
    """
    Extract color, texture, spot density, and shape features from image pixels.
    Returns normalized feature vector of fixed size (16 elements).
    """
    total_px = len(pixels)
    if total_px == 0:
        return [0.0] * 16

    # 1. Global Color Means & Std
    r_vals = [p[0] / 255.0 for p in pixels]
    g_vals = [p[1] / 255.0 for p in pixels]
    b_vals = [p[2] / 255.0 for p in pixels]

    mean_r = sum(r_vals) / total_px
    mean_g = sum(g_vals) / total_px
    mean_b = sum(b_vals) / total_px

    std_r = math.sqrt(sum((x - mean_r) ** 2 for x in r_vals) / total_px)
    std_g = math.sqrt(sum((x - mean_g) ** 2 for x in g_vals) / total_px)
    std_b = math.sqrt(sum((x - mean_b) ** 2 for x in b_vals) / total_px)

    # 2. Leaf vs Background Segmentation (Background is bright soil/beige)
    leaf_pixels = [p for p in pixels if not (p[0] > 210 and p[1] > 200 and p[2] > 190)]
    leaf_ratio = len(leaf_pixels) / total_px

    if len(leaf_pixels) > 0:
        leaf_r = sum(p[0] / 255.0 for p in leaf_pixels) / len(leaf_pixels)
        leaf_g = sum(p[1] / 255.0 for p in leaf_pixels) / len(leaf_pixels)
        leaf_b = sum(p[2] / 255.0 for p in leaf_pixels) / len(leaf_pixels)
    else:
        leaf_r, leaf_g, leaf_b = mean_r, mean_g, mean_b

    # 3. Spot & Lesion Detection
    dark_spot_count = sum(1 for p in pixels if p[0] < 80 and p[1] < 80 and p[2] < 60) / total_px
    yellow_patch_count = sum(1 for p in pixels if p[0] > 170 and p[1] > 160 and p[2] < 100) / total_px
    green_healthy_count = sum(1 for p in pixels if p[1] > p[0] + 30 and p[1] > p[2] + 30) / total_px

    # 4. Spatial Distribution (Quadrants)
    half_w, half_h = width // 2, height // 2
    quadrants = [0.0] * 5  # Q1, Q2, Q3, Q4, Center

    for y in range(height):
        for x in range(width):
            px = pixels[y * width + x]
            if not (px[0] > 210 and px[1] > 200 and px[2] > 190):
                if x < half_w and y < half_h: quadrants[0] += 1
                elif x >= half_w and y < half_h: quadrants[1] += 1
                elif x < half_w and y >= half_h: quadrants[2] += 1
                elif x >= half_w and y >= half_h: quadrants[3] += 1
                if abs(x - half_w) < half_w // 2 and abs(y - half_h) < half_h // 2:
                    quadrants[4] += 1

    quadrants = [q / (total_px / 4) for q in quadrants]

    return [
        mean_r, mean_g, mean_b,
        std_r, std_g, std_b,
        leaf_ratio, leaf_r, leaf_g, leaf_b,
        dark_spot_count, yellow_patch_count, green_healthy_count,
        quadrants[0], quadrants[1], quadrants[4]
    ]

def relu(x: list[float]) -> list[float]:
    return [max(0.0, v) for v in x]

def softmax(x: list[float]) -> list[float]:
    max_val = max(x)
    exp_vals = [math.exp(v - max_val) for v in x]
    sum_exp = sum(exp_vals)
    return [v / (sum_exp + 1e-12) for v in exp_vals]
