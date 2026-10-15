"""
Frontmatter YAML Formatter for Doc2MD.
Generates structured metadata headers (YAML frontmatter) tailored for
Obsidian, Notion, Logseq, and personal note-taking workspaces.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import yaml


SUPPORTED_PRESETS = ["none", "obsidian", "notion", "minimal"]


def has_frontmatter(markdown_text: str) -> bool:
    """Checks whether the markdown string already begins with a YAML frontmatter block."""
    if not markdown_text:
        return False
    return bool(re.match(r'^---\s*\r?\n.*?\r?\n---\s*(\r?\n|$)', markdown_text.lstrip(), re.DOTALL))


def extract_frontmatter(markdown_text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parses existing frontmatter from markdown text if present.
    Returns (metadata_dict, remaining_body_text).
    """
    if not markdown_text:
        return None, ""

    stripped = markdown_text.lstrip()
    match = re.match(r'^---\s*\r?\n(.*?)\r?\n---\s*(\r?\n|$)(.*)', stripped, re.DOTALL)
    if not match:
        return None, markdown_text

    raw_yaml, _, body = match.groups()
    try:
        data = yaml.safe_load(raw_yaml)
        if isinstance(data, dict):
            return data, body.lstrip()
    except Exception:
        pass

    return None, markdown_text


def strip_frontmatter(markdown_text: str) -> str:
    """Removes existing YAML frontmatter block from markdown text, returning only the body."""
    _, body = extract_frontmatter(markdown_text)
    return body


def build_frontmatter_dict(
    filename: str,
    token_count: int = 0,
    char_count: int = 0,
    preset: str = "obsidian",
    extra_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Constructs a clean metadata dictionary according to the chosen preset."""
    clean_preset = (preset or "obsidian").strip().lower()
    base_title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").strip()
    ext = os.path.splitext(filename)[1].lstrip(".").lower() or "doc"
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now_date = datetime.now().strftime("%Y-%m-%d")

    tags = ["doc2md", ext]
    if extra_tags:
        for t in extra_tags:
            clean_t = re.sub(r'[^a-zA-Z0-9_\-]', '', str(t)).strip().lower()
            if clean_t and clean_t not in tags:
                tags.append(clean_t)

    if clean_preset == "notion":
        return {
            "Title": base_title,
            "Source File": filename,
            "Created Date": now_date,
            "Tokens": token_count,
            "Characters": char_count,
            "Status": "Converted",
            "Tags": [t.title() for t in tags],
        }
    elif clean_preset == "minimal":
        return {
            "title": base_title,
            "source": filename,
            "date": now_date,
        }
    else:
        # Default to Obsidian preset
        return {
            "title": base_title,
            "source": filename,
            "created": now_iso,
            "tokens": token_count,
            "characters": char_count,
            "tags": tags,
            "aliases": [base_title],
        }


def format_frontmatter_block(metadata: Dict[str, Any]) -> str:
    """Dumps a metadata dictionary into formatted YAML frontmatter enclosed in '---'."""
    yaml_str = yaml.dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False
    ).strip()
    return f"---\n{yaml_str}\n---"


def attach_frontmatter(
    markdown_text: str,
    filename: str,
    token_count: int = 0,
    char_count: int = 0,
    preset: str = "obsidian",
    extra_tags: Optional[List[str]] = None
) -> str:
    """
    Strips any existing frontmatter and attaches a freshly formatted
    YAML frontmatter header to the markdown text.
    If preset is 'none', returns the text as-is.
    """
    clean_preset = (preset or "obsidian").strip().lower()
    if clean_preset in ("none", "off", "disabled", "false"):
        return markdown_text

    body = strip_frontmatter(markdown_text)
    calculated_char_count = char_count or len(body)
    meta = build_frontmatter_dict(
        filename=filename,
        token_count=token_count,
        char_count=calculated_char_count,
        preset=clean_preset,
        extra_tags=extra_tags
    )
    fm_header = format_frontmatter_block(meta)
    return f"{fm_header}\n\n{body}"
