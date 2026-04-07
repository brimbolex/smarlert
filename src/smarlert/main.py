from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from smarlert.config import AppConfig, load_config
from smarlert.extractor import extract_value
from smarlert.fetcher import fetch_content


def load_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_state(path: Path, state: dict[str, str]) -> None:
    path.write_text(json.dumps(state, indent=2) + "\n")


def send_signal(config: AppConfig, message: str) -> None:
    command = [
        config.signal.signal_cli_path,
        "-u",
        config.signal.account,
        "send",
        "-m",
        message,
    ]

    if config.signal.group_id:
        command.extend(["-g", config.signal.group_id])
    else:
        command.append(config.signal.recipient or "")

    subprocess.run(command, check=True)


def build_message(config: AppConfig, new_value: str, old_value: str | None) -> str:
    if old_value is None:
        return f"[{config.job_name}] Initial value detected: {new_value}"
    return f"[{config.job_name}] Change detected\nOld: {old_value}\nNew: {new_value}"


def run(config: AppConfig, dry_run: bool = False) -> int:
    state_path = Path(config.state_file)
    state = load_state(state_path)

    raw_body = fetch_content(config.source)
    current_value = extract_value(raw_body, config.source.format, config.source.extract)
    previous_value = state.get("last_value")

    if previous_value == current_value:
        print("No change detected.")
        return 0

    message = build_message(config, current_value, previous_value)
    if dry_run:
        print(message)
    else:
        send_signal(config, message)
    save_state(state_path, {"last_value": current_value})
    if dry_run:
        print("Change detected. Dry run only, no Signal message sent.")
    else:
        print("Change detected and notification sent.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect website data and send Signal alerts")
    parser.add_argument("--config", default="config.json", help="Path to the JSON config file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the message instead of sending it to Signal",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    return run(config, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
