import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import config
from routes.form_description import router as form_router
from routes.media_description import router as media_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(config.TEMP_IMAGES_DIR, exist_ok=True)
    os.makedirs(config.TEMP_DOCUMENTS_DIR, exist_ok=True)
    yield


app = FastAPI(title="SoapBox AI Assist", lifespan=lifespan)

app.include_router(form_router)
app.include_router(media_router)
