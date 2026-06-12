import json
from fastapi import UploadFile
from services.media_description.media_description_orchestrator import orchestrate


async def handle_media_description(
    module: str,
    data_str: str,
    images: list[UploadFile] | None,
    document: UploadFile | None,
) -> dict:
    has_images = bool(images)
    has_document = document is not None

    if not has_images and not has_document:
        return {
            "error": "No media provided. At least one image or document is required.",
            "status": 400,
        }

    if has_images and has_document:
        return {
            "error": "Provide either images or a document, not both.",
            "status": 400,
        }

    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in 'data' field.", "status": 400}

    try:
        description = await orchestrate(
            module=module,
            data=data,
            images=images if has_images else None,
            document=document if has_document else None,
        )
        return {"description": description}
    except ValueError as e:
        return {"error": str(e), "status": 400}
    except Exception as e:
        return {"error": f"Internal error: {str(e)}", "status": 500}
