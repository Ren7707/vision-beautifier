from __future__ import annotations

import math
from pathlib import Path

import numpy as np


def _cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("缺少 opencv-python，请先安装 requirements.txt") from exc
    return cv2


def read_image(path: str | Path, grayscale: bool = False) -> np.ndarray:
    cv2 = _cv2()
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), flag)
    if img is None:
        raise ValueError(f"无法读取图片：{path}")
    return img if grayscale else cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def save_image(path: str | Path, img: np.ndarray) -> None:
    cv2 = _cv2()
    ext = Path(path).suffix or ".png"
    data = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(ext, data)
    if not ok:
        raise ValueError(f"无法保存图片：{path}")
    Path(path).write_bytes(buf.tobytes())


def _u8(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, 0, 255).astype(np.uint8)


def adjust_brightness_contrast(img: np.ndarray, brightness: int = 0, contrast: float = 1.0) -> np.ndarray:
    return _u8(img.astype(np.float32) * contrast + brightness)


def crop_region(img: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    h, w = img.shape[:2]
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(w, x1 + max(1, width)), min(h, y1 + max(1, height))
    return img[y1:y2, x1:x2].copy()


def add_noise(img: np.ndarray, kind: str, amount: float = 0.04) -> np.ndarray:
    rng = np.random.default_rng()
    if kind == "gaussian":
        return _u8(img.astype(np.float32) + rng.normal(0, amount * 255, img.shape))
    if kind == "salt_pepper":
        out = img.copy()
        mask = rng.random(img.shape[:2])
        out[mask < amount / 2] = 0
        out[mask > 1 - amount / 2] = 255
        return out
    if kind == "uniform":
        return _u8(img.astype(np.float32) + rng.uniform(-amount * 255, amount * 255, img.shape))
    raise ValueError(f"未知噪声类型：{kind}")


def denoise(img: np.ndarray, method: str, ksize: int = 5) -> np.ndarray:
    cv2 = _cv2()
    ksize = max(3, ksize | 1)
    if method == "mean":
        return cv2.blur(img, (ksize, ksize))
    if method == "median":
        return cv2.medianBlur(img, ksize)
    if method == "gaussian":
        return cv2.GaussianBlur(img, (ksize, ksize), 0)
    raise ValueError(f"未知去噪方法：{method}")


def rotate(img: np.ndarray, angle: float) -> np.ndarray:
    cv2 = _cv2()
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, m, (w, h))


def flip(img: np.ndarray, mode: str) -> np.ndarray:
    if mode == "horizontal":
        return np.flip(img, axis=1).copy()
    if mode == "vertical":
        return np.flip(img, axis=0).copy()
    return np.flip(np.flip(img, axis=0), axis=1).copy()


def translate(img: np.ndarray, dx: int, dy: int) -> np.ndarray:
    cv2 = _cv2()
    h, w = img.shape[:2]
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, m, (w, h))


def adjust_hsv(img: np.ndarray, hue: int = 0, saturation: float = 1.0) -> np.ndarray:
    cv2 = _cv2()
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] + hue) % 180
    hsv[..., 1] = np.clip(hsv[..., 1] * saturation, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)


def sharpen(img: np.ndarray) -> np.ndarray:
    cv2 = _cv2()
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(img, -1, kernel)


def outline(img: np.ndarray) -> np.ndarray:
    cv2 = _cv2()
    gray = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 80, 160)
    out = img.copy() if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    out[edges > 0] = [20, 20, 20]
    return out


def add_border(img: np.ndarray, size: int = 24, color: tuple[int, int, int] = (245, 220, 150)) -> np.ndarray:
    cv2 = _cv2()
    return cv2.copyMakeBorder(img, size, size, size, size, cv2.BORDER_CONSTANT, value=color)


def emboss(img: np.ndarray) -> np.ndarray:
    cv2 = _cv2()
    kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]], dtype=np.float32)
    return _u8(cv2.filter2D(img, -1, kernel) + 96)


def fog(img: np.ndarray, strength: float = 0.28) -> np.ndarray:
    white = np.full_like(img, 255)
    return _u8(img.astype(np.float32) * (1 - strength) + white.astype(np.float32) * strength)


def add_text(img: np.ndarray, text: str = "Vision", x: int = 32, y: int = 64) -> np.ndarray:
    cv2 = _cv2()
    out = img.copy()
    cv2.putText(out, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 80, 40), 3, cv2.LINE_AA)
    return out


def threshold_mask(img: np.ndarray) -> np.ndarray:
    cv2 = _cv2()
    gray = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask


def grabcut_mask(img: np.ndarray, rect: tuple[int, int, int, int]) -> np.ndarray:
    cv2 = _cv2()
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
    return np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)


def apply_mask(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros_like(img)
    out[mask > 0] = img[mask > 0]
    return out


def measure_mask(mask: np.ndarray) -> dict[str, float | tuple[float, float]]:
    binary = mask > 0
    area = int(binary.sum())
    if area == 0:
        return {"area": 0, "centroid": (0.0, 0.0), "perimeter": 0.0, "rectangularity": 0.0, "circularity": 0.0}

    ys, xs = np.nonzero(binary)
    centroid = (round(float(xs.mean()), 2), round(float(ys.mean()), 2))
    bbox_area = (int(xs.max() - xs.min()) + 1) * (int(ys.max() - ys.min()) + 1)

    padded = np.pad(binary.astype(np.uint8), 1)
    center = padded[1:-1, 1:-1]
    perimeter = int(((center == 1) & (padded[:-2, 1:-1] == 0)).sum())
    perimeter += int(((center == 1) & (padded[2:, 1:-1] == 0)).sum())
    perimeter += int(((center == 1) & (padded[1:-1, :-2] == 0)).sum())
    perimeter += int(((center == 1) & (padded[1:-1, 2:] == 0)).sum())

    circularity = 0.0 if perimeter == 0 else 4 * math.pi * area / (perimeter * perimeter)
    return {
        "area": area,
        "centroid": centroid,
        "perimeter": round(float(perimeter), 2),
        "rectangularity": round(area / bbox_area, 4),
        "circularity": round(circularity, 4),
    }
