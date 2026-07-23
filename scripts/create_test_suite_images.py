import os
import math
import random
import struct
from pathlib import Path

TEST_DIR = Path("Backend/data/plantvillage_subset/test")

def generate_bmp(width: int, height: int, pixels: list[tuple[int, int, int]]) -> bytes:
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    image_size = (row_bytes + padding) * height
    offset = 54
    file_size = offset + image_size

    file_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, offset)
    dib_header = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0, image_size, 2835, 2835, 0, 0)

    pixel_bytes = bytearray()
    pad_bytes = b"\x00" * padding

    for y in range(height - 1, -1, -1):
        row_start = y * width
        for x in range(width):
            r, g, b = pixels[row_start + x]
            pixel_bytes.extend((b, g, r))
        pixel_bytes.extend(pad_bytes)

    return bytes(file_header + dib_header + pixel_bytes)

def create_sample_leaf(class_name: str, width: int = 224, height: int = 224) -> bytes:
    bg_r, bg_g, bg_b = 230, 225, 215
    pixels = [(bg_r, bg_g, bg_b)] * (width * height)
    center_x, center_y = width // 2, height // 2

    spots = []
    if class_name == "cotton_bacterial_blight":
        for _ in range(20):
            spots.append({"x": random.randint(60, 160), "y": random.randint(60, 160), "r": random.randint(4, 9), "color": (30, 15, 10), "halo": (200, 190, 40)})
    elif class_name == "cotton_curl_virus":
        for _ in range(15):
            spots.append({"x": random.randint(50, 170), "y": random.randint(50, 170), "r": random.randint(8, 18), "color": (210, 215, 70), "halo": None})
    elif class_name == "tomato_late_blight":
        for _ in range(10):
            spots.append({"x": random.randint(60, 160), "y": random.randint(60, 160), "r": random.randint(10, 24), "color": (45, 30, 20), "halo": (120, 130, 40)})
    elif class_name == "tomato_leaf_mold":
        for _ in range(18):
            spots.append({"x": random.randint(50, 170), "y": random.randint(50, 170), "r": random.randint(6, 14), "color": (210, 185, 60), "halo": None})

    for y in range(height):
        for x in range(width):
            dx, dy = x - center_x, y - center_y
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)

            is_leaf = False
            base_color = (0, 0, 0)

            if "cotton" in class_name:
                max_r = 75 * (0.8 + 0.35 * math.sin(5 * angle))
                if dist <= max_r:
                    is_leaf = True
                    base_color = (34, 139, 34) if "healthy" in class_name else (65, 115, 45) if class_name == "cotton_bacterial_blight" else (125, 145, 55)
            else:
                rx, ry = 50 * (0.9 + 0.2 * math.sin(7 * angle)), 80 * (0.9 + 0.2 * math.sin(3 * angle))
                if math.hypot(dx / (rx + 1e-5), dy / (ry + 1e-5)) <= 1.0:
                    is_leaf = True
                    base_color = (46, 139, 87) if "healthy" in class_name else (70, 90, 40) if class_name == "tomato_late_blight" else (135, 135, 50)

            if is_leaf:
                final_color = base_color
                for spot in spots:
                    s_dist = math.hypot(x - spot["x"], y - spot["y"])
                    if spot["halo"] and s_dist <= spot["r"] + 3:
                        final_color = spot["halo"]
                    if s_dist <= spot["r"]:
                        final_color = spot["color"]
                        break
                pixels[y * width + x] = final_color

    return generate_bmp(width, height, pixels)

def create_non_leaf_image(width: int = 224, height: int = 224) -> bytes:
    """Generate non-leaf abstract pattern."""
    pixels = []
    for y in range(height):
        for x in range(width):
            r = (x * 255) // width
            g = (y * 255) // height
            b = ((x + y) * 255) // (width + height)
            pixels.append((r, g, b))
    return generate_bmp(width, height, pixels)

def create_dark_blurry_image(width: int = 224, height: int = 224) -> bytes:
    """Generate low brightness image."""
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels.append((25, 30, 20))
    return generate_bmp(width, height, pixels)

def main():
    print("Creating sample test images in Backend/data/plantvillage_subset/test/...")
    os.makedirs(TEST_DIR, exist_ok=True)

    test_cases = [
        ("test_cotton_healthy.bmp", create_sample_leaf("cotton_healthy")),
        ("test_cotton_bacterial_blight.bmp", create_sample_leaf("cotton_bacterial_blight")),
        ("test_cotton_curl_virus.bmp", create_sample_leaf("cotton_curl_virus")),
        ("test_tomato_healthy.bmp", create_sample_leaf("tomato_healthy")),
        ("test_tomato_late_blight.bmp", create_sample_leaf("tomato_late_blight")),
        ("test_tomato_leaf_mold.bmp", create_sample_leaf("tomato_leaf_mold")),
        ("test_non_leaf.bmp", create_non_leaf_image()),
        ("test_dark_blurry.bmp", create_dark_blurry_image()),
    ]

    for fname, data in test_cases:
        path = TEST_DIR / fname
        with open(path, "wb") as f:
            f.write(data)
        print(f"Created {path} ({len(data)} bytes)")

if __name__ == "__main__":
    main()
