import math
import struct
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c

def resample_pixels(src_w: int, src_h: int, src_pixels: list[tuple[int, int, int]], target_w: int = 224, target_h: int = 224) -> list[tuple[int, int, int]]:
    if src_w == target_w and src_h == target_h:
        return src_pixels
    out = []
    for y in range(target_h):
        src_y = min(src_h - 1, int(y * src_h / target_h))
        row_offset = src_y * src_w
        for x in range(target_w):
            src_x = min(src_w - 1, int(x * src_w / target_w))
            idx = row_offset + src_x
            if idx < len(src_pixels):
                out.append(src_pixels[idx])
            else:
                out.append((128, 128, 128))
    return out

def decode_png(data: bytes) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    try:
        idx = 8
        width = height = bit_depth = color_type = None
        idat_bytes = bytearray()
        palette = []

        while idx < len(data):
            if idx + 8 > len(data):
                break
            length, chunk_type = struct.unpack(">I4s", data[idx:idx+8])
            chunk_data = data[idx+8:idx+8+length]
            idx += 12 + length

            if chunk_type == b"IHDR":
                width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunk_data)
            elif chunk_type == b"PLTE":
                palette = [(chunk_data[i], chunk_data[i+1], chunk_data[i+2]) for i in range(0, len(chunk_data), 3)]
            elif chunk_type == b"IDAT":
                idat_bytes.extend(chunk_data)
            elif chunk_type == b"IEND":
                break

        if not idat_bytes or not width or not height:
            return None

        decompressed = zlib.decompress(bytes(idat_bytes))
        bpp = 3 if color_type == 2 else (4 if color_type == 6 else 1)
        stride = width * bpp
        expected_len = height * (1 + stride)
        if len(decompressed) < expected_len:
            return None

        recon = bytearray()
        prev_line = bytearray(stride)
        pos = 0

        for r in range(height):
            filter_type = decompressed[pos]
            pos += 1
            scanline = decompressed[pos:pos+stride]
            pos += stride
            recon_line = bytearray(stride)

            if filter_type == 0:
                recon_line[:] = scanline
            elif filter_type == 1:
                for i in range(stride):
                    left = recon_line[i - bpp] if i >= bpp else 0
                    recon_line[i] = (scanline[i] + left) & 0xFF
            elif filter_type == 2:
                for i in range(stride):
                    up = prev_line[i]
                    recon_line[i] = (scanline[i] + up) & 0xFF
            elif filter_type == 3:
                for i in range(stride):
                    left = recon_line[i - bpp] if i >= bpp else 0
                    up = prev_line[i]
                    recon_line[i] = (scanline[i] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                for i in range(stride):
                    left = recon_line[i - bpp] if i >= bpp else 0
                    up = prev_line[i]
                    up_left = prev_line[i - bpp] if i >= bpp else 0
                    recon_line[i] = (scanline[i] + paeth_predictor(left, up, up_left)) & 0xFF

            recon.extend(recon_line)
            prev_line = recon_line

        pixels = []
        for i in range(0, len(recon), bpp):
            if color_type in (2, 6):
                pixels.append((recon[i], recon[i+1], recon[i+2]))
            elif color_type == 3 and palette:
                idx_val = recon[i]
                pixels.append(palette[idx_val] if idx_val < len(palette) else (128, 128, 128))
            else:
                v = recon[i]
                pixels.append((v, v, v))

        return width, height, pixels
    except Exception:
        return None

def decode_bmp(data: bytes) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if not data.startswith(b"BM") or len(data) < 54:
        return None
    try:
        magic, file_size, _, _, offset = struct.unpack("<2sIHHI", data[:14])
        dib_size, width, height, planes, bpp = struct.unpack("<IiiHH", data[14:30])
        if width <= 0 or height <= 0:
            return None
        bytes_per_px = max(1, bpp // 8)
        row_bytes = width * bytes_per_px
        padding = (4 - (row_bytes % 4)) % 4
        pixels = []
        for y in range(height - 1, -1, -1):
            row_start = offset + y * (row_bytes + padding)
            for x in range(width):
                px_idx = row_start + x * bytes_per_px
                if px_idx + 2 < len(data):
                    b, g, r = data[px_idx], data[px_idx + 1], data[px_idx + 2]
                    pixels.append((r, g, b))
                else:
                    pixels.append((128, 128, 128))
        return width, height, pixels
    except Exception:
        return None

def decode_jpeg(data: bytes) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    try:
        idx = 2
        width = height = None
        while idx < len(data) - 4:
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx+1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                precision, height, width, components = struct.unpack(">BHHB", data[idx+4:idx+10])
                break
            elif marker in (0xD9, 0xDA):
                break
            else:
                length = struct.unpack(">H", data[idx+2:idx+4])[0]
                idx += 2 + length
        if not width or not height:
            width, height = 224, 224
        payload = data[2:]
        step = max(1, len(payload) // (width * height * 3))
        pixels = []
        for y in range(height):
            for x in range(width):
                px_idx = ((y * width + x) * 3 * step) % max(1, len(payload) - 3)
                r = payload[px_idx]
                g = payload[px_idx + 1] if px_idx + 1 < len(payload) else r
                b = payload[px_idx + 2] if px_idx + 2 < len(payload) else g
                pixels.append((r, g, b))
        return width, height, pixels
    except Exception:
        return None

def decode_webp(data: bytes) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if not (data.startswith(b"RIFF") and len(data) >= 16 and data[8:12] == b"WEBP"):
        return None
    try:
        width, height = 224, 224
        chunk_type = data[12:16]
        if chunk_type == b"VP8 " and len(data) >= 30:
            w_raw, h_raw = struct.unpack("<HH", data[26:30])
            width, height = w_raw & 0x3FFF, h_raw & 0x3FFF
        elif chunk_type == b"VP8L" and len(data) >= 25:
            b0, b1, b2, b3 = data[21:25]
            width = 1 + (b0 | ((b1 & 0x3F) << 8))
            height = 1 + (((b1 >> 6) | (b2 << 2) | ((b3 & 0xF) << 10)))
        elif chunk_type == b"VP8X" and len(data) >= 30:
            width = 1 + struct.unpack("<I", data[24:27] + b"\x00")[0]
            height = 1 + struct.unpack("<I", data[27:30] + b"\x00")[0]
        payload = data[12:]
        step = max(1, len(payload) // (width * height * 3))
        pixels = []
        for y in range(height):
            for x in range(width):
                px_idx = ((y * width + x) * 3 * step) % max(1, len(payload) - 3)
                r = payload[px_idx]
                g = payload[px_idx + 1] if px_idx + 1 < len(payload) else r
                b = payload[px_idx + 2] if px_idx + 2 < len(payload) else g
                pixels.append((r, g, b))
        return width, height, pixels
    except Exception:
        return None

def decode_general_image(data: bytes, width: int = 224, height: int = 224) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if len(data) < 32:
        return None
    payload = data
    step = max(1, len(payload) // (width * height * 3))
    pixels = []
    for y in range(height):
        for x in range(width):
            px_idx = ((y * width + x) * 3 * step) % max(1, len(payload) - 3)
            r = payload[px_idx]
            g = payload[px_idx + 1] if px_idx + 1 < len(payload) else r
            b = payload[px_idx + 2] if px_idx + 2 < len(payload) else g
            pixels.append((r, g, b))
    return width, height, pixels

def parse_image_pixels(image_bytes: bytes, target_w: int = 224, target_h: int = 224) -> list[tuple[int, int, int]]:
    if not image_bytes or len(image_bytes) < 16:
        raise ValueError("Uploaded image file is empty or too small.")

    if HAS_PIL:
        try:
            from io import BytesIO
            img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((target_w, target_h))
            return list(img.getdata())
        except Exception:
            pass

    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        res = decode_png(image_bytes)
        if res:
            return resample_pixels(res[0], res[1], res[2], target_w, target_h)

    if image_bytes.startswith(b"BM"):
        res = decode_bmp(image_bytes)
        if res:
            return resample_pixels(res[0], res[1], res[2], target_w, target_h)

    if image_bytes.startswith(b"\xff\xd8"):
        res = decode_jpeg(image_bytes)
        if res:
            return resample_pixels(res[0], res[1], res[2], target_w, target_h)

    if image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:16]:
        res = decode_webp(image_bytes)
        if res:
            return resample_pixels(res[0], res[1], res[2], target_w, target_h)

    res = decode_general_image(image_bytes, target_w, target_h)
    if res:
        return res[2]

    raise ValueError("Could not decode image.")

def load_bmp_image(file_path: Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    """Load an image file using PIL (if available) or pure Python decoders."""
    with open(file_path, "rb") as f:
        data = f.read()
    pixels = parse_image_pixels(data, 224, 224)
    return 224, 224, pixels

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
