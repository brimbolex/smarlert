# smarlert

Small alerting tool that collects data from a website and pushes updates to a Signal chat.

## What it does

- Fetches HTML or JSON from a target website
- Extracts values with CSS selectors, regex, or JSON paths
- Stores the last result locally
- Sends a Signal message only when the result changes

## Stack

- Python 3.11+
- `requests` for fetching
- `beautifulsoup4` for HTML parsing
- `signal-cli` for sending messages to Signal

## Quick start

1. Create a virtual environment and install dependencies.
2. Copy `config.example.json` to `config.json`.
3. Update the website config and Signal chat settings.
4. Make sure `signal-cli` is installed and linked to your Signal account.
5. Run the notifier.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m smarlert.main --config config.json
```

Test extraction without sending a Signal message:

```bash
python3 -m smarlert.main --config config.json --dry-run
```

## Signal setup

This project sends messages with `signal-cli`, because Signal does not provide a general public bot API for arbitrary chats.

Example registration flow:

```bash
signal-cli -u +15551234567 register
signal-cli -u +15551234567 verify 123-456
```

Group chats use a `group_id`. Direct chats use a recipient phone number.

## Config example

```json
{
  "job_name": "Example monitor",
  "source": {
    "url": "https://example.com/status",
    "method": "GET",
    "format": "html",
    "headers": {
      "User-Agent": "smarlert/1.0"
    },
    "extract": {
      "type": "css",
      "selector": ".status",
      "attribute": "text"
    }
  },
  "signal": {
    "account": "+15551234567",
    "recipient": "+15557654321"
  },
  "state_file": ".smarlert-state.json"
}
```

## Extraction modes

- `css`: Extract from HTML with a CSS selector. Use `attribute: "text"` for inner text.
- `regex`: Extract from the raw response body with a regex.
- `json_path`: Extract from JSON using dot-separated keys like `data.items.0.name`.
- `today_date`: Extract the date immediately following a visible `Heute` marker in page text.

## Residenztheater example

The included [config.example.json](/Users/alex/Documents/CODE/smarlert/config.example.json) is already set up for `https://www.residenztheater.de/spielplan` and extracts only the date shown under `Heute`.

On April 7, 2026, that visible date is `7 Apr` on the site. Source: https://www.residenztheater.de/spielplan

## Scheduling

Run this script from cron, launchd, systemd, or GitHub Actions on a schedule.

Cron example:

```bash
*/10 * * * * cd /Users/alex/Documents/CODE/smarlert && /usr/bin/env bash -lc 'source .venv/bin/activate && python3 -m smarlert.main --config config.json'
```

## Notes

- Respect the website's terms, robots policy, and rate limits.
- If the target site requires JavaScript rendering, this version will need a browser automation step added later.
