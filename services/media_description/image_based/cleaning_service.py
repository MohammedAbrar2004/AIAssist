from PIL import Image, ImageEnhance

MAX_DIM = 1024


def preprocess_image(image_path: str) -> Image.Image:
    img = Image.open(image_path).convert("RGB")

    # Resize: cap longest edge to MAX_DIM
    w, h = img.size
    if max(w, h) > MAX_DIM:
        scale = MAX_DIM / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Mild contrast enhancement
    img = ImageEnhance.Contrast(img).enhance(1.2)

    return img
