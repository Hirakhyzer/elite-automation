"""Scheduling utilities for social media posts."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol, Sequence

from .content import PostCopy
from .design import DesignTemplate

_MAX_SLEEP_SECONDS = 300.0


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
        else:
            run_at = run_at.astimezone(timezone.utc)
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

    async def _wait_until(self, run_at: datetime) -> None:
        """Wait in bounded chunks so cancellation and clock changes are re-evaluated."""
        while True:
            remaining = (run_at - datetime.now(tz=timezone.utc)).total_seconds()
            if remaining <= 0:
                return
            await asyncio.sleep(min(remaining, _MAX_SLEEP_SECONDS))

    async def dispatch(self, autoposter: "AutoPosterProtocol") -> None:
        try:
            for schedule in self.queue:
                await self._wait_until(schedule.run_at)
                await autoposter.post(schedule.copy, schedule.design)
        finally:
            self.queue.clear()


class AutoPosterProtocol(Protocol):
    async def post(self, copy: PostCopy, design: DesignTemplate) -> None:
        ...
