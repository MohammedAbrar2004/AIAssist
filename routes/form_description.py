from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.request_models import FormDescriptionRequest
from controllers.form_description_controller import handle_form_description

router = APIRouter()


@router.post("/api/formDescription")
async def form_description(request: FormDescriptionRequest):
    result = handle_form_description(request)
    if "error" in result:
        return JSONResponse(content=result, status_code=result.get("status", 400))
    return result
