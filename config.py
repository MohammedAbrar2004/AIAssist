import os

# --- Groq API ---
GROQ_API_KEY = ''

# --- LLM Models ---
SUMMARIZATION_MODEL = "llama-3.3-70b-versatile"   # Used for document summarization
DESCRIPTION_MODEL = "llama-3.1-8b-instant"         # Used for generating form/media descriptions

# --- Vision Models ---
BLIP_MODEL = "Salesforce/blip-image-captioning-base"
YOLO_MODEL = "yolov8n.pt"

# --- Media Limits ---
MAX_IMAGES = 10
MAX_IMAGE_SIZE_MB = 10
MAX_DOCUMENT_SIZE_MB = 50
SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
SUPPORTED_DOCUMENT_TYPES = ["application/pdf",
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# --- Temp Storage ---
TEMP_IMAGES_DIR = "services/media_description/temp/images"
TEMP_DOCUMENTS_DIR = "services/media_description/temp/documents"
