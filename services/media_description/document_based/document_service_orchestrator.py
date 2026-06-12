import pdfplumber
from docx import Document
from groq import Groq
import config

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _extract_text(doc_path: str, mime_type: str) -> str:
    if mime_type == "application/pdf":
        with pdfplumber.open(doc_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif mime_type == _DOCX_MIME:
        doc = Document(doc_path)
        return "\n".join(para.text for para in doc.paragraphs)
    return ""


def _summarize(text: str, module: str) -> str:
    client = Groq(api_key=config.GROQ_API_KEY)
    prompt = (
        f"You are an EHS (Environment, Health & Safety) analyst reviewing a {module} document.\n"
        f"Summarize the following content concisely, highlighting key EHS findings and facts:\n\n{text}"
    )
    response = client.chat.completions.create(
        model=config.SUMMARIZATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def process_document(doc_path: str, mime_type: str, module: str) -> dict:
    text = _extract_text(doc_path, mime_type)
    if not text.strip():
        return {"summary": "No text content found in document."}
    summary = _summarize(text, module)
    return {"summary": summary}
