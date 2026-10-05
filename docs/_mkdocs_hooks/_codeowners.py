import logging
import re
from pathlib import Path

logger = logging.getLogger("mkdocs.codeowners")

ROOT_DIR = Path(__file__).parent.parent.parent
CODEOWNERS_PATHS = [ROOT_DIR / ".github" / "CODEOWNERS", ROOT_DIR / "CODEOWNERS", ROOT_DIR / "docs" / "CODEOWNERS"]
H1_PATTERN = re.compile(r"^# .+$", re.MULTILINE)

_rules = []


def _pattern_to_regex(pattern: str) -> re.Pattern:
    anchored = pattern.startswith("/") or "/" in pattern.rstrip("/")
    pattern = pattern.lstrip("/")
    dir_only = pattern.endswith("/")
    pattern = pattern.rstrip("/")
    out = ""
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if pattern[i : i + 3] == "**/":
            out += "(?:.*/)?"
            i += 3
            continue
        if pattern[i : i + 2] == "**":
            out += ".*"
            i += 2
            continue
        if c == "*":
            out += "[^/]*"
        elif c == "?":
            out += "[^/]"
        else:
            out += re.escape(c)
        i += 1
    prefix = "" if anchored else "(?:.*/)?"
    suffix = "/.*" if dir_only else "(?:/.*)?"
    return re.compile(f"^{prefix}{out}{suffix}$")


def _load_rules():
    _rules.clear()
    path = next((p for p in CODEOWNERS_PATHS if p.exists()), None)
    if path is None:
        logger.warning("No CODEOWNERS file found.")
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        pattern, *owners = line.split()
        if owners:
            _rules.append((_pattern_to_regex(pattern), owners))


def on_pre_build(config, **kwargs):
    _load_rules()


def get_owners(rel_path: str):
    owners = []
    for regex, rule_owners in _rules:  # last matching rule wins
        if regex.match(rel_path):
            owners = rule_owners
    return owners


def on_page_markdown(markdown, page, config, **kwargs):
    if not _rules:
        _load_rules()
    src = page.file.src_path.replace("\\", "/")
    owners = get_owners(f"docs/{src}")
    if not owners:
        return markdown
    links = ", ".join(
        f"[{o}](https://github.com/{o.lstrip('@')})" if o.startswith("@") and "/" not in o else o
        for o in owners
    )
    line = f"\n\n**Code owners:** {links}"
    match = H1_PATTERN.search(markdown)
    if not match:
        return f"**Code owners:** {links}\n\n{markdown}"
    return markdown[: match.end()] + line + markdown[match.end() :]
