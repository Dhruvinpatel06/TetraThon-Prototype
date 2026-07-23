import os
import json
import math
import random
import struct
from pathlib import Path

CLASSES = [
    "cotton_bacterial_blight",
    "cotton_curl_virus",
    "cotton_healthy",
    "tomato_late_blight",
    "tomato_leaf_mold",
    "tomato_healthy"
]

DATASET_DIR = Path("Backend/data/plantvillage_subset")

def create_bmp_leaf(class_name: str, width: int = 224, height: int = 224) -> bytes:
    """
    Generate 24-bit uncompressed BMP leaf image in pure Python (zero external dependencies).
    """
    # Background (soil / light neutral tone)
    bg_r = 230 + random.randint(-10, 10)
    bg_g = 225 + random.randint(-10, 10)
    bg_b = 215 + random.randint(-10, 10)

    pixels = [(bg_r, bg_g, bg_b)] * (width * height)

    center_x = width // 2
    center_y = height // 2

    # Disease spot parameters
    spots = []
    if class_name == "cotton_bacterial_blight":
        # Angular dark brown necrotic spots with yellow halos
        for _ in range(random.randint(12, 25)):
            spots.append({
                "x": random.randint(60, 160),
                "y": random.randint(60, 160),
                "r": random.randint(4, 9),
                "color": (30, 15, 10),
                "halo": (200, 190, 40)
            })
    elif class_name == "cotton_curl_virus":
        # Yellowing vein lesions and leaf distortion
        for _ in range(random.randint(10, 20)):
            spots.append({
                "x": random.randint(50, 170),
                "y": random.randint(50, 170),
                "r": random.randint(8, 18),
                "color": (210, 215, 70),
                "halo": None
            })
    elif class_name == "tomato_late_blight":
        # Large dark brown water-soaked lesions
        for _ in range(random.randint(6, 14)):
            spots.append({
                "x": random.randint(60, 160),
                "y": random.randint(60, 160),
                "r": random.randint(10, 24),
                "color": (45, 30, 20),
                "halo": (120, 130, 40)
            })
    elif class_name == "tomato_leaf_mold":
        # Pale yellow patches
        for _ in range(random.randint(10, 22)):
            spots.append({
                "x": random.randint(50, 170),
                "y": random.randint(50, 170),
                "r": random.randint(6, 14),
                "color": (210, 185, 60),
                "halo": None
            })

    # Render pixel grid
    for y in range(height):
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            dist = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)

            is_leaf = False
            base_color = (0, 0, 0)

            if "cotton" in class_name:
                # Palmate lobed leaf (5 lobes)
                max_r = 75 * (0.8 + 0.35 * math.sin(5 * angle))
                if dist <= max_r:
                    is_leaf = True
                    if "healthy" in class_name:
                        base_color = (34, 139, 34)
                    elif class_name == "cotton_bacterial_blight":
                        base_color = (65, 115, 45)
                    else:
                        base_color = (125, 145, 55)
            else:
                # Tomato leaf shape (elongated pinnate with serrated edge)
                rx = 50 * (0.9 + 0.2 * math.sin(7 * angle))
                ry = 80 * (0.9 + 0.2 * math.sin(3 * angle))
                normalized_dist = math.hypot(dx / (rx + 1e-5), dy / (ry + 1e-5))
                if normalized_dist <= 1.0:
                    is_leaf = True
                    if "healthy" in class_name:
                        base_color = (46, 139, 87)
                    elif class_name == "tomato_late_blight":
                        base_color = (70, 90, 40)
                    else:
                        base_color = (135, 135, 50)

            if is_leaf:
                final_color = base_color
                # Check spots
                for spot in spots:
                    s_dist = math.hypot(x - spot["x"], y - spot["y"])
                    if spot["halo"] and s_dist <= spot["r"] + 3:
                        final_color = spot["halo"]
                    if s_dist <= spot["r"]:
                        final_color = spot["color"]
                        break

                pixels[y * width + x] = final_color

    # Convert to BMP binary bytes
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

def main():
    print("Preparing PlantVillage subset dataset (BMP format)...")
    os.makedirs(DATASET_DIR, exist_ok=True)

    samples_per_class = 60
    total_generated = 0

    for cls in CLASSES:
        cls_dir = DATASET_DIR / cls
        os.makedirs(cls_dir, exist_ok=True)

        for i in range(1, samples_per_class + 1):
            bmp_data = create_bmp_leaf(cls)
            img_path = cls_dir / f"image_{i:03d}.bmp"
            with open(img_path, "wb") as f:
                f.write(bmp_data)
            total_generated += 1

    print(f"Generated {total_generated} BMP images across {len(CLASSES)} classes in {DATASET_DIR}")

    # Verify images
    valid_count = 0
    corrupt_count = 0

    for cls in CLASSES:
        cls_dir = DATASET_DIR / cls
        for img_path in cls_dir.glob("*.bmp"):
            try:
                with open(img_path, "rb") as f:
                    data = f.read()
                assert len(data) == 54 + 224 * 224 * 3, "Invalid BMP file size"
                assert data[:2] == b"BM", "Invalid BMP magic header"
                valid_count += 1
            except Exception as e:
                print(f"Corrupt image detected: {img_path} - {e}")
                corrupt_count += 1

    print(f"Dataset verification complete: {valid_count} valid, {corrupt_count} corrupt.")

    class_names_path = Path("Backend/models/class_names.json")
    if class_names_path.exists():
        with open(class_names_path) as f:
            names = json.load(f)
        print(f"Loaded class_names.json: {names}")
    else:
        print("WARNING: Backend/models/class_names.json not found!")

if __name__ == "__main__":
    main()
