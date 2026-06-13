# Elite Automation

Automation toolkit that designs creatives, writes copy, schedules content, and posts to social media channels. The project delivers a modular Python package and CLI so you can plug in your own connectors or run in preview mode while iterating on messaging.

## Features

- **Auto write** – configurable strategies generate headlines, captions, and hashtags tailored to an audience persona.
- **Auto design** – lightweight branding-aware image generator with optional Pillow support. Falls back to design metadata when Pillow is unavailable.
- **Auto schedule** – import ISO-8601 timestamps and queue posts for future publication.
- **Auto post** – pluggable connector system with built-in mock and webhook destinations, ready for extension to real APIs.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[design]  # optional Pillow-powered image assets
```

## Command Line Usage

Generate two posts in preview mode:

```bash
elite-automation --preview --strategy promotional --audience marketer launch update
```

Run with a configuration file (`config.json`) and schedule (`schedule.json`):

```bash
elite-automation --config config.json --schedule schedule.json automation ai
```

### Sample `config.json`

```json
{
  "connectors": {
    "mock": {"type": "mock"},
    "launch-webhook": {
      "type": "webhook",
      "endpoint": "https://example.com/webhook",
      "credentials": {"token": "API_TOKEN"}
    }
  }
}
```

### Sample `schedule.json`

```json
{
  "topics": [
    {"run_at": "2024-08-01T14:00:00+00:00"},
    {"run_at": "2024-08-02T14:00:00+00:00"}
  ]
}
```

## Extending

1. Create a new connector by subclassing `elite_automation.connectors.base.SocialConnector`.
2. Register the connector in `elite_automation.poster._CONNECTOR_TYPES`.
3. Reference it in your configuration JSON with any required credentials.

This design keeps writing, design, scheduling, and posting concerns separated, enabling you to swap pieces without rewriting the entire automation flow.
