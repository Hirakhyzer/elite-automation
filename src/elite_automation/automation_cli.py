"""Command line interface for the Elite Automation toolkit."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Iterable

from .content import AutoWriter, ContentStrategy
from .design import AutoDesigner
from .poster import AutoPoster
from .scheduler import Scheduler


def load_json(path: Path | None) -> dict | None:
    if path is None:
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate social media content generation and scheduling.",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="educational",
        help="Content strategy name (educational, promotional, announcement).",
    )
    parser.add_argument(
        "--audience",
        type=str,
        default="general",
        help="Audience persona keyword for tone adaptation.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON configuration file for connectors.",
    )
    parser.add_argument(
        "--schedule",
        type=Path,
        default=None,
        help="Optional JSON file describing scheduled posts.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print posts instead of sending them to connectors.",
    )
    parser.add_argument(
        "topics",
        nargs="*",
        default=("automation", "productivity"),
        help="Topics to generate content for.",
    )
    return parser.parse_args(argv)


async def main_async(namespace: argparse.Namespace) -> None:
    writer = AutoWriter(ContentStrategy.from_name(namespace.strategy))
    designer = AutoDesigner()
    scheduler = Scheduler()

    schedule_data = load_json(namespace.schedule)
    config_data = load_json(namespace.config)

    autoposter = await AutoPoster.create(config_data or {}, preview=namespace.preview)

    posts = []
    for topic in namespace.topics:
        copy = writer.generate_post(topic=topic, audience=namespace.audience)
        design = designer.create_design(topic=topic, message=copy.headline)
        posts.append((copy, design))

    if schedule_data:
        scheduler.import_schedule(schedule_data, posts)
        await scheduler.dispatch(autoposter)
    else:
        for copy, design in posts:
            await autoposter.post(copy, design)


def main(argv: Iterable[str] | None = None) -> None:
    namespace = parse_args(argv)
    asyncio.run(main_async(namespace))


if __name__ == "__main__":
    main()
