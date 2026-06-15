# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SoapBox AI Assist is a FastAPI engine that exposes AI capabilities as REST endpoints consumed by Oracle APEX for an EHS (Environment, Health & Safety) platform. It automates form description writing and media interpretation.

## Environment Setup

- Python 3.11, Conda environment named `AiAssist`
- Activate: `conda activate AiAssist`
- Install dependencies: `pip install -r requirements.txt`
- Run dev server: `uvicorn main:app --reload`
- Set required env var: `GROQ_API_KEY`

No test suite or linter is configured yet.

## Architecture

Two REST endpoints, each with its own route → controller → service stack:

**`POST /api/formDescription`** — JSON input with `module` + `data` fields → loads prompt template → calls Groq LLM → returns `{ "description": "..." }`

**`POST /api/mediaDescription`** — multipart/form-data with `module`, `data` (JSON string), optional `images` (up to 10) and/or `document` (1 PDF/DOCX) → saves to temp → runs image or document pipeline → combines outputs → calls Groq LLM → cleans up temp → returns `{ "description": "..." }`

### Image Pipeline
Each image goes through `cleaning_service.py` (resize + contrast), then YOLO and BLIP run **in parallel** via `concurrent.futures`. `image_service_orchestrator.py` aggregates all captions and detected objects across images.

### Document Pipeline
`document_service_orchestrator.py` extracts text via pdfplumber (PDF) or python-docx (DOCX), then summarizes with `llama-3.3-70b-versatile` before feeding into the final description prompt.

## Key Conventions

- All configurable settings (model names, API keys, size limits, temp dirs) live in `config.py` — never hardcode elsewhere.
- MIME type detection is the source of truth for pipeline routing, not file extensions.
- The `data` field in the media endpoint arrives as a JSON string — parse before use.
- Temp files use deterministic naming: `{module}_{timestamp}_{index}.{ext}`. Cleanup always runs in `finally` blocks.
- BLIP and YOLO models are lazy-loaded at startup via lifespan handlers in `main.py`.
- Unsupported modules return HTTP 400.

## LLM Models

| Purpose | Model |
|---|---|
| Form/media description | `llama-3.1-8b-instant` |
| Document summarization | `llama-3.3-70b-versatile` |

## Deferred Components

These are intentionally placeholder/incomplete — implement only when explicitly asked:
- `services/master_context_service.py` — universal EHS context for all modules
- `prompts/form/*.txt` — prompt templates for form description (incident, risk, capa)
- `prompts/media/*.txt` — prompt templates for media description (incident, risk, capa)

## Reference Folder

A `reference/` folder contains an older implementation of form description and image-based media description. Use it **only as a reference** — do not copy directly. The canonical implementation lives in `AI_Assist/`.
