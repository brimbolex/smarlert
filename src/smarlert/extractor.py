from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

from smarlert.config import ExtractConfig


def extract_value(raw_body: str, response_format: str, extract: ExtractConfig | None) -> str:
    if extract is None:
        return raw_body.strip()

    if extract.type == "today_date":
        return _extract_today_date(raw_body)
    if extract.type == "css":
        return _extract_css(raw_body, extract)
    if extract.type == "regex":
        return _extract_regex(raw_body, extract)
    if extract.type == "json_path":
        if response_format != "json":
            raise ValueError("json_path extraction requires source.format=json")
        return _extract_json_path(raw_body, extract)

    raise ValueError(f"Unsupported extraction type: {extract.type}")


def _extract_css(raw_body: str, extract: ExtractConfig) -> str:
    if not extract.selector:
        raise ValueError("css extraction requires selector")

    soup = BeautifulSoup(raw_body, "html.parser")
    node = soup.select_one(extract.selector)
    if node is None:
        raise ValueError(f"CSS selector did not match: {extract.selector}")

    if extract.attribute and extract.attribute != "text":
        value = node.get(extract.attribute)
        if value is None:
            raise ValueError(
                f"Attribute '{extract.attribute}' not found for selector {extract.selector}"
            )
        return str(value).strip()

    return node.get_text(" ", strip=True)


def _extract_regex(raw_body: str, extract: ExtractConfig) -> str:
    if not extract.pattern:
        raise ValueError("regex extraction requires pattern")

    match = re.search(extract.pattern, raw_body, re.MULTILINE | re.DOTALL)
    if match is None:
        raise ValueError(f"Regex did not match: {extract.pattern}")
    return match.group(extract.group).strip()


def _extract_json_path(raw_body: str, extract: ExtractConfig) -> str:
    if not extract.path:
        raise ValueError("json_path extraction requires path")

    current: Any = json.loads(raw_body)
    for part in extract.path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return str(current).strip()


def _extract_today_date(raw_body: str) -> str:
    text = BeautifulSoup(raw_body, "html.parser").get_text("\n", strip=True)
    patterns = [
        r"Heute\s+(\d{1,2}\s+[A-Za-z]{3,})",
        r"Heute\s+[A-Za-z]+\s+([A-Za-z]{2}\.\s+\d{1,2}\s+[A-Za-z]{3,})",
        r"Heute\s+\d{1,2}\s+[A-Za-z]{3,}\s+[A-Za-z]+\s+([A-Za-z]{2}\.\s+\d{1,2}\s+[A-Za-z]{3,})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match is not None:
            return match.group(1).strip()

    raise ValueError("Could not find today's date after the 'Heute' marker")
