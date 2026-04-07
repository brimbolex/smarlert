from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExtractConfig:
    type: str
    selector: str | None = None
    attribute: str | None = None
    pattern: str | None = None
    group: int = 1
    path: str | None = None


@dataclass(slots=True)
class SourceConfig:
    url: str
    method: str = "GET"
    format: str = "html"
    timeout_seconds: int = 20
    headers: dict[str, str] | None = None
    payload: dict[str, Any] | None = None
    extract: ExtractConfig | None = None


@dataclass(slots=True)
class SignalConfig:
    account: str
    recipient: str | None = None
    group_id: str | None = None
    signal_cli_path: str = "signal-cli"


@dataclass(slots=True)
class AppConfig:
    job_name: str
    source: SourceConfig
    signal: SignalConfig
    state_file: str = ".smarlert-state.json"


def _require(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing required config key: {key}")
    return mapping[key]


def load_config(path: str | Path) -> AppConfig:
    data = json.loads(Path(path).read_text())

    source_data = _require(data, "source")
    signal_data = _require(data, "signal")
    extract_data = source_data.get("extract")

    extract = None
    if extract_data is not None:
        extract = ExtractConfig(
            type=_require(extract_data, "type"),
            selector=extract_data.get("selector"),
            attribute=extract_data.get("attribute"),
            pattern=extract_data.get("pattern"),
            group=extract_data.get("group", 1),
            path=extract_data.get("path"),
        )

    source = SourceConfig(
        url=_require(source_data, "url"),
        method=source_data.get("method", "GET"),
        format=source_data.get("format", "html"),
        timeout_seconds=source_data.get("timeout_seconds", 20),
        headers=source_data.get("headers"),
        payload=source_data.get("payload"),
        extract=extract,
    )

    signal = SignalConfig(
        account=_require(signal_data, "account"),
        recipient=signal_data.get("recipient"),
        group_id=signal_data.get("group_id"),
        signal_cli_path=signal_data.get("signal_cli_path", "signal-cli"),
    )

    if not signal.recipient and not signal.group_id:
        raise ValueError("Signal config requires either recipient or group_id")

    return AppConfig(
        job_name=data.get("job_name", "smarlert"),
        source=source,
        signal=signal,
        state_file=data.get("state_file", ".smarlert-state.json"),
    )
