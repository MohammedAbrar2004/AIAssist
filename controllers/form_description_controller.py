from models.request_models import FormDescriptionRequest
from services.master_context_service import get_master_context
from services.form_description import prompt_service, llm_service


def handle_form_description(request: FormDescriptionRequest) -> dict:
    try:
        master_context = get_master_context()
        prompt = prompt_service.build_prompt(request.module, request.data, master_context)
        description = llm_service.generate_description(prompt)
        return {"description": description}
    except ValueError as e:
        return {"error": str(e), "status": 400}
    except Exception as e:
        return {"error": f"Internal error: {str(e)}", "status": 500}
