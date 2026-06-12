# CLAUDE.md — SoapBox AI Assist

## Project Overview

**SoapBox AI Assist** is an AI engine built for a cloud-native EHS (Environment, Health & Safety)
platform. It exposes AI capabilities as REST API endpoints consumed by Oracle APEX. The engine
enhances user experience by automating tedious tasks like writing form descriptions and
interpreting uploaded media.

The engine currently supports two services:
1. **Form Description Generation** — generates contextual form descriptions from structured input fields
2. **Media Description Generation** — generates descriptions from uploaded images and/or documents alongside form context

Both services are exposed as **standalone REST API endpoints** built with FastAPI.

---

## Tech Stack

| Component | Tool / Library |
|---|---|
| Language | Python 3.11 |
| Virtual Environment | Conda — env name: `AiAssist` |
| Web Framework | FastAPI |
| ASGI Server | Uvicorn |
| LLM Provider | Groq API |
| Image Captioning | BLIP — `Salesforce/blip-image-captioning-base` (via `transformers`) |
| Object Detection | YOLOv8 nano — `yolov8n.pt` (via `ultralytics`) |
| Deep Learning Backend | PyTorch (CPU-compatible, BLIP + YOLO compatible version) |
| Image Preprocessing | Pillow |
| PDF Text Extraction | pdfplumber |
| DOCX Text Extraction | python-docx |
| Multipart Form Parsing | python-multipart |
| Data Validation | Pydantic v2 |
| Async Parallelism | asyncio / concurrent.futures (for BLIP + YOLO parallel execution) |

**Compatible version constraints to respect:**
- `transformers` version must be compatible with `Salesforce/blip-image-captioning-base`
- `ultralytics` version must support YOLOv8 nano (`yolov8n.pt`)
- `torch` version must be compatible with both BLIP and YOLO dependencies

---

## Configuration — `config.py`

All environment-sensitive and model-related settings live in `config.py`. These must remain
editable and never be hardcoded elsewhere.

```python
# config.py

import os

# --- Groq API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

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
```

---

## File Structure

```
Ai_Assist/
│
├── main.py                         ← FastAPI app entry point
├── config.py                       ← Env vars, model names, settings
├── requirements.txt
│
├── routes/                         ← API route definitions
│   ├── form_description.py
│   └── media_description.py
│
├── controllers/                    ← Request/response handling logic
│   ├── form_description_controller.py
│   └── media_description_controller.py
│
├── services/
│   │
│   ├── form_description/
│   │   ├── prompt_service.py       ← Loads prompt template, injects form data
│   │   └── llm_service.py          ← Calls Groq API for description generation
│   │
│   ├── media_description/
│   │   ├── temp/                   ← Temporary file storage (cleaned after each request)
│   │   │   ├── images/
│   │   │   └── documents/
│   │   │
│   │   ├── image_based/
│   │   │   ├── cleaning_service.py              ← Mild image preprocessing
│   │   │   ├── yolo_service.py                  ← YOLOv8 object detection
│   │   │   ├── blip_service.py                  ← BLIP image captioning
│   │   │   └── image_service_orchestrator.py    ← Runs YOLO + BLIP in parallel, combines output
│   │   │
│   │   ├── document_based/
│   │   │   └── document_service_orchestrator.py ← Extraction + summarization pipeline
│   │   │
│   │   ├── prompt_service.py                    ← Loads media prompt template, injects all context
│   │   ├── media_description_orchestrator.py    ← Main orchestrator: saves files, routes pipelines
│   │   └── llm_service.py                       ← Calls Groq API for final media description
│   │
│   └── master_context_service.py   ← [Defined last] Loads universal EHS context for all modules
│
├── prompts/                        ← [Defined last] Module-specific prompt templates
│   ├── form/
│   │   ├── incident.txt
│   │   ├── risk.txt
│   │   └── capa.txt
│   └── media/
│       ├── incident.txt
│       ├── risk.txt
│       └── capa.txt
│
└── models/
    └── request_models.py           ← Pydantic request/response schemas
```

---

## Use Case 1 — Form Description Generation

### API Endpoint

```
POST /api/formDescription
Content-Type: application/json
```

### Request

```json
{
  "module": "incident",
  "data": {
    "incident_type": "Fire",
    "location": "Plant A",
    "severity": "High",
    "reported_by": "John Doe"
  }
}
```

### Response

```json
{
  "description": "A high-severity fire incident was reported at Plant A by John Doe. ..."
}
```

### Error Response

```json
{
  "error": "Unsupported module: 'xyz'",
  "status": 400
}
```

### Data Contracts

| Field | Type | Required | Description |
|---|---|---|---|
| `module` | `string` | Yes | EHS module name (e.g., `"incident"`, `"risk"`, `"capa"`) |
| `data` | `object` | Yes | Key-value pairs of form fields specific to the module |

### Internal Flow

```
POST /api/formDescription
        ↓
form_description_controller.py
        ↓
Module Router → validate module name → select prompt template from /prompts/form/<module>.txt
        ↓
master_context_service.py → load universal EHS master context
        ↓
prompt_service.py → inject form data fields + master context into prompt template
        ↓
llm_service.py → Groq API (llama-3.1-8b-instant)
        ↓
Return { "description": "..." }
```

---

## Use Case 2 — Media Description Generation

### API Endpoint

```
POST /api/mediaDescription
Content-Type: multipart/form-data
```

### Request

```
module:   incident                          (string, form field)
data:     {                                 (JSON string, form field)
            "incident_type": "Fire",
            "location": "Plant A",
            "severity": "High",
            "reported_by": "John Doe"
          }
images:   fire1.jpg                         (file, optional — up to 10)
          fire2.jpg
document: fire_incident_report.pdf          (file, optional — max 1)
```

> At least one of `images` or `document` must be present in the request not both.

### Response

```json
{
  "description": "The uploaded images show signs of a fire incident at an industrial facility. ..."
}
```

### Error Response

```json
{
  "error": "No media provided. At least one image or document is required.",
  "status": 400
}
```

### Data Contracts

| Field | Type | Required | Constraints |
|---|---|---|---|
| `module` | `string` | Yes | Must match a supported module |
| `data` | `JSON string` | Yes | Parsed into dict; module-specific fields |
| `images` | `List[UploadFile]` | Conditional | Max 10 files; MIME: `image/jpeg`, `image/png`, `image/webp` |
| `document` | `UploadFile` | Conditional | Max 1 file; MIME: `application/pdf` or `.docx` |

### Internal Flow (Top-Level Orchestration)

```
POST /api/mediaDescription
        ↓
media_description_controller.py
        ↓
media_description_orchestrator.py
  ├── Save uploaded files to temp/ with deterministic naming convention
  ├── Detect MIME type of each file
  ├── Route to Image Pipeline   (if images present)
  └── Route to Document Pipeline (if document present)
        ↓
Collect outputs: image_output, document_output
        ↓
master_context_service.py → load master context
        ↓
prompt_service.py → inject module context + form fields + image_output + document_output
        ↓
llm_service.py → Groq API (llama-3.1-8b-instant)
        ↓
Cleanup temp files
        ↓
Return { "description": "..." }
```

### Image Pipeline

```
List of images (up to 10)
        ↓
cleaning_service.py
  └── Mild preprocessing per image: resize, normalize, contrast enhancement
        ↓ (parallel per image)
  ┌─────────────────────────────────────┐
  │ yolo_service.py                     │
  │   └── YOLOv8 nano → detected objects│
  └─────────────────────────────────────┘
  ┌─────────────────────────────────────┐
  │ blip_service.py                     │
  │   └── BLIP → caption per image      │
  └─────────────────────────────────────┘
        ↓
image_service_orchestrator.py
  └── Combine YOLO + BLIP output across all images

Returns:
{
  "captions": ["A fire burning near industrial equipment", "Smoke in a corridor"],
  "objects_detected": ["fire", "smoke", "extinguisher", "person"]
}
```

### Document Pipeline

```
Single document (PDF or DOCX)
        ↓
document_service_orchestrator.py
  ├── Identify MIME type
  ├── PDF  → pdfplumber  → extracted plain text
  └── DOCX → python-docx → extracted plain text
        ↓
Groq API (llama-3.3-70b-versatile) → summarize extracted text within module context

Returns:
{
  "summary": "The report documents a fire incident at Plant A on [date]. Key findings include ..."
}
```

---

## Temp File Naming Convention

Temp files are saved before processing and cleaned up after each request.

| Type | Pattern |
|---|---|
| Images | `{module}_{timestamp}_{index}.{ext}` e.g. `incident_20240612_1.jpg` |
| Documents | `{module}_{timestamp}.{ext}` e.g. `incident_20240612.pdf` |

Cleanup must always run — including on exceptions (use `finally` blocks).

---

## Deferred Components

The following are intentionally left to be written at the end of the project:

- **`master_context_service.py`** — universal EHS master context (field descriptions, domain
  terminology, field type semantics) loaded for every module
- **`/prompts/form/*.txt`** — module-specific prompt templates for form description generation
- **`/prompts/media/*.txt`** — module-specific prompt templates for media description generation

---

## General Conventions

- Groq API key must always be loaded from environment or `config.py` — never hardcoded
- MIME type detection is the source of truth for pipeline routing — do not rely on file extensions
- YOLO and BLIP are run in **parallel** per image using `asyncio` or `concurrent.futures`
- `data` field in the media endpoint arrives as a **JSON string** and must be parsed before use
- All modules must have a corresponding prompt template — unknown modules return a 400 error
- Temp directory must be created on startup if it does not exist
- Reference folder contains existing logic for form description and image-based media description — use it as the source of truth when implementing those services. 
We need to start implementation from scratch inside AI_Assist folder.
Reference folder is an old implementation to only be used for refernece

