import os

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "form")
SUPPORTED_MODULES = {"incident", "risk", "capa"}


def build_prompt(module: str, data: dict, master_context: str) -> str:
    if module not in SUPPORTED_MODULES:
        raise ValueError(f"Unsupported module: '{module}'")

    template_path = os.path.join(PROMPTS_DIR, f"{module}.txt")
    with open(template_path, "r") as f:
        template = f.read()

    form_data_str = "\n".join(f"- {k}: {v}" for k, v in data.items())

    return template.format(
        form_data=form_data_str,
        master_context=master_context,
    )
