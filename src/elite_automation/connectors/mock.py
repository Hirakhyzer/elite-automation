"""Mock connectors for development and testing."""

from __future__ import annotations

import asyncio
from typing import Any

from .base import PostPayload, SocialConnector


class MockConnector(SocialConnector):
    """A connector that prints payloads instead of posting."""

    def __init__(self, name: str = "mock"):
        super().__init__(name=name)

    async def authenticate(self, **credentials: Any) -> None:  # pragma: no cover - trivial
        await asyncio.sleep(0)

    async def publish(self, payload: PostPayload) -> None:
        await asyncio.sleep(0)
        rendered = payload.copy.render()
        print(f"[{self.name.upper()}] Posting copy:\n{rendered}")
        if payload.design.output_path:
            print(f"[{self.name.upper()}] Using asset at {payload.design.output_path}")
        else:
            print(f"[{self.name.upper()}] Design palette: {payload.design.to_dict()}")
