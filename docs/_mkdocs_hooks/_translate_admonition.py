import re

ADMONITION_MAP = {
    "NOTE": "note",
    "TIP": "tip",
    "IMPORTANT": "important",
    "WARNING": "warning",
    "CAUTION": "caution",
    "DANGER": "danger",
    "ERROR": "failure",   # MkDocs Material uses "failure"
    "SUCCESS": "success",
    "QUESTION": "question",
}

def on_page_markdown(markdown, **kwargs):
    pattern = re.compile(r"^> \[!(\w+)\]\s*\n((?:^> .*(?:\n|$))*)", re.MULTILINE)

    def repl(match):
        kind_raw = match.group(1).upper()
        kind = ADMONITION_MAP.get(kind_raw, kind_raw.lower())
        content = re.sub(r"^> ?", "", match.group(2), flags=re.MULTILINE).rstrip()
        indented = "\n    ".join(content.splitlines())
        return f"!!! {kind}\n    {indented}"

    return pattern.sub(repl, markdown)
