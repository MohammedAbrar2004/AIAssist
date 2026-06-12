from groq import Groq
import config

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def generate_description(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=config.DESCRIPTION_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
