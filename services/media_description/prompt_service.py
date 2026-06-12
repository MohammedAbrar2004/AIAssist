import os

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "media")
SUPPORTED_MODULES = {"incident", "risk", "capa"}


def build_prompt(
    module: str,
    data: dict,
    master_context: str,
    image_output: dict | None,
    document_output: dict | None,
) -> str:
    if module not in SUPPORTED_MODULES:
        raise ValueError(f"Unsupported module: '{module}'")

    template_path = os.path.join(PROMPTS_DIR, f"{module}.txt")
    with open(template_path, "r") as f:
        template = f.read()

    form_data_str = "\n".join(f"- {k}: {v}" for k, v in data.items())

    if image_output:
        captions_str = "\n".join(f"  - {c}" for c in image_output.get("captions", []))
        objects_str = ", ".join(image_output.get("objects_detected", []))
        image_section = f"Captions:\n{captions_str}\nDetected Objects: {objects_str}"
    else:
        image_section = "No image evidence provided."

    doc_section = document_output.get("summary", "") if document_output else "No document evidence provided."

    return template.format(
        form_data=form_data_str,
        master_context=master_context,
        image_output=image_section,
        document_output=doc_section,
    )
