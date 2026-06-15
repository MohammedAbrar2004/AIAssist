import re
from groq import Groq
import config

_client: Groq | None = None

_VARIATION_INSTRUCTION = """
---

Generate exactly 3 variations of the description, each using only the fields provided above. Vary the tone and phrasing — not the facts. Do not add any information not present in the Form Data.

[1] CONCISE: Direct and brief — state the key facts in as few words as possible.
[2] PROFESSIONAL: Formal register, as it would appear in an official EHS report.
[3] NARRATIVE: Flowing, contextual phrasing — still strictly factual, no added content.

Respond in this exact format — no additional text before or after:
[1] <description>
[2] <description>
[3] <description>
"""


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def _parse_descriptions(raw: str) -> list[str]:
    matches = re.findall(r'\[\d\]\s*(.*?)(?=\[\d\]|$)', raw.strip(), re.DOTALL)
    descriptions = [m.strip() for m in matches if m.strip()]
    return descriptions[:3] if descriptions else [raw.strip()]


def generate_descriptions(prompt: str) -> list[str]:
    client = _get_client()
    response = client.chat.completions.create(
        model=config.DESCRIPTION_MODEL,
        messages=[{"role": "user", "content": prompt + _VARIATION_INSTRUCTION}]
    )
    raw = response.choices[0].message.content.strip()
    return _parse_descriptions(raw)
