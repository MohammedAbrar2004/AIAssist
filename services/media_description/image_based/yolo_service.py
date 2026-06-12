from ultralytics import YOLO
from PIL import Image
import config

_model: YOLO | None = None


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO(config.YOLO_MODEL)
    return _model


def detect_objects(image: Image.Image) -> list[str]:
    model = _get_model()
    results = model(image, verbose=False)

    objects: set[str] = set()
    for result in results:
        for box in result.boxes:
            label = result.names[int(box.cls[0])]
            objects.add(label)

    return list(objects)
