from pydantic import BaseModel


class FormDescriptionRequest(BaseModel):
    module: str
    data: dict


class FormDescriptionResponse(BaseModel):
    descriptions: list[str]


class ErrorResponse(BaseModel):
    error: str
    status: int
