from __future__ import annotations

import json

import requests

from smarlert.config import SourceConfig


def fetch_content(source: SourceConfig) -> str:
    response = requests.request(
        method=source.method,
        url=source.url,
        headers=source.headers,
        json=source.payload,
        timeout=source.timeout_seconds,
    )
    response.raise_for_status()

    if source.format == "json":
        return json.dumps(response.json())
    return response.text
