#!/usr/bin/env python3
import yaml
from typing import Dict, Any
from pathlib import Path
import logging
import re

logging.basicConfig(format="%(levelname)-8s - %(message)s", level=logging.INFO)
logger = logging.getLogger("mkdocs.navbuilder")

ROOT_DIR = Path(__file__).parent.parent
DOCS_DIR = ROOT_DIR / "docs"
MKDOCS_YML = ROOT_DIR / "mkdocs.yml"


def format_title(text: str) -> str:
    words = re.sub(r"[_-]", " ", text).split()
    return " ".join(word.capitalize() for word in words)


def on_pre_build(config: Dict[str, Any]) -> None:
    if MKDOCS_YML.exists():
        with open(MKDOCS_YML, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    config["nav"] = build_nav(DOCS_DIR)

    with open(MKDOCS_YML, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False)
    logger.info(f"✅ Updated {MKDOCS_YML} with {len(config['nav'])} nav entries.")


def build_nav(path: Path):
    """
    Recursively build a nested MkDocs nav structure from Markdown files.
    """
    nav = []
    entries = sorted([p.name for p in path.iterdir()])

    if "index.md" in entries:
        entries.remove("index.md")
        entries.insert(0, "index.md")

    for entry in entries:
        full_path = path / entry
        if full_path.is_dir():
            sub_nav = build_nav(full_path)
            if sub_nav:
                nav.append({format_title(entry): sub_nav})
        elif entry.endswith(".md"):
            rel_path = full_path.relative_to(DOCS_DIR).as_posix()
            title = format_title(full_path.stem)
            nav.append({title: rel_path})
    return nav


if __name__ == "__main__":
    if not MKDOCS_YML.exists():
        logger.error(f"❌ {MKDOCS_YML} does not exist. Please create it first.")
    else:
        with open(MKDOCS_YML, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        on_pre_build(config)
        logger.info("✅ MkDocs nav updated successfully.")
