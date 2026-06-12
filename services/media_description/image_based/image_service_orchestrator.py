from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from services.media_description.image_based.cleaning_service import preprocess_image
from services.media_description.image_based.yolo_service import detect_objects
from services.media_description.image_based.blip_service import generate_caption


def _process_single_image(image_path: str) -> dict:
    image: Image.Image = preprocess_image(image_path)

    with ThreadPoolExecutor(max_workers=2) as executor:
        yolo_future = executor.submit(detect_objects, image)
        blip_future = executor.submit(generate_caption, image)
        objects = yolo_future.result()
        caption = blip_future.result()

    return {"objects": objects, "caption": caption}


def process_images(image_paths: list[str]) -> dict:
    all_captions: list[str] = []
    all_objects: set[str] = set()

    for path in image_paths:
        result = _process_single_image(path)
        all_captions.append(result["caption"])
        all_objects.update(result["objects"])

    return {
        "captions": all_captions,
        "objects_detected": list(all_objects),
    }
