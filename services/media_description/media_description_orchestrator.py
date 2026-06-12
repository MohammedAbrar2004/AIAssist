import os
import json
from datetime import datetime
from fastapi import UploadFile
import filetype
import config
from services.master_context_service import get_master_context
from services.media_description.image_based.image_service_orchestrator import process_images
from services.media_description.document_based.document_service_orchestrator import process_document
from services.media_description import prompt_service, llm_service


async def _save_file(upload_file: UploadFile, dest_path: str) -> None:
    content = await upload_file.read()
    with open(dest_path, "wb") as f:
        f.write(content)


def _detect_mime(file_path: str, fallback: str) -> str:
    kind = filetype.guess(file_path)
    if kind:
        # DOCX is a ZIP archive — filetype reports application/zip; use fallback if it matches supported types
        if kind.mime == "application/zip" and fallback in config.SUPPORTED_DOCUMENT_TYPES:
            return fallback
        return kind.mime
    return fallback


async def orchestrate(
    module: str,
    data: dict,
    images: list[UploadFile] | None,
    document: UploadFile | None,
) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_image_paths: list[str] = []
    saved_doc_path: str | None = None

    try:
        if images:
            os.makedirs(config.TEMP_IMAGES_DIR, exist_ok=True)
            for i, img in enumerate(images):
                ext = os.path.splitext(img.filename or "")[1] or ".jpg"
                filename = f"{module}_{timestamp}_{i + 1}{ext}"
                path = os.path.join(config.TEMP_IMAGES_DIR, filename)
                await _save_file(img, path)
                saved_image_paths.append(path)

        if document:
            os.makedirs(config.TEMP_DOCUMENTS_DIR, exist_ok=True)
            ext = os.path.splitext(document.filename or "")[1] or ".pdf"
            filename = f"{module}_{timestamp}{ext}"
            saved_doc_path = os.path.join(config.TEMP_DOCUMENTS_DIR, filename)
            await _save_file(document, saved_doc_path)

        image_output = process_images(saved_image_paths) if saved_image_paths else None

        document_output = None
        if saved_doc_path:
            mime = _detect_mime(saved_doc_path, document.content_type or "")
            document_output = process_document(saved_doc_path, mime, module)

        master_context = get_master_context()
        prompt = prompt_service.build_prompt(module, data, master_context, image_output, document_output)
        return llm_service.generate_description(prompt)

    finally:
        for path in saved_image_paths:
            if os.path.exists(path):
                os.remove(path)
        if saved_doc_path and os.path.exists(saved_doc_path):
            os.remove(saved_doc_path)
