from typing import List, Optional
from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse
from controllers.media_description_controller import handle_media_description

router = APIRouter()


@router.post("/api/mediaDescription")
async def media_description(
    module: str = Form(...),
    data: str = Form(...),
    images: Optional[List[UploadFile]] = File(default=None),
    document: Optional[UploadFile] = File(default=None),
):
    result = await handle_media_description(module, data, images, document)
    if "error" in result:
        return JSONResponse(content=result, status_code=result.get("status", 400))
    return result
