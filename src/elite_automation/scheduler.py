"""Scheduling utilities for social media posts."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence

from .content import PostCopy
from .design import DesignTemplate


@dataclass(order=True)
class Schedule:
    """Scheduled post information."""

    run_at: datetime
    copy: PostCopy = field(compare=False)
    design: DesignTemplate = field(compare=False)

    @staticmethod
    def parse(timestamp: str, copy: PostCopy, design: DesignTemplate) -> "Schedule":
        run_at = datetime.fromisoformat(timestamp)
        if run_at.tzinfo is None:
            run_at = run_at.replace(tzinfo=timezone.utc)
        return Schedule(run_at=run_at, copy=copy, design=design)


class Scheduler:
    """Simple in-memory scheduler for posting flows."""

    def __init__(self):
        self.queue: list[Schedule] = []

    def import_schedule(
        self, schedule_data: dict, generated_posts: Sequence[tuple[PostCopy, DesignTemplate]]
    ) -> None:
        topics = schedule_data.get("topics", [])
        for item, generated in zip(topics, generated_posts):
            timestamp = item.get("run_at")
            if not timestamp:
                continue
            schedule = Schedule.parse(timestamp, copy=generated[0], design=generated[1])
            self.queue.append(schedule)
        self.queue.sort()

    async def dispatch(self, autoposter: "AutoPosterProtocol") -> None:
        for schedule in self.queue:
            now = datetime.now(tz=timezone.utc)
            if schedule.run_at > now:
                await asyncio.sleep((schedule.run_at - now).total_seconds())
            await autoposter.post(schedule.copy, schedule.design)
        self.queue.clear()


class AutoPosterProtocol:
    async def post(self, copy: PostCopy, design: DesignTemplate) -> None:  # pragma: no cover - protocol
        ...
