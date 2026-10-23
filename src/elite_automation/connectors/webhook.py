"""Webhook-based connector implementation."""

from __future__ import annotations

import asyncio
import json
from functools import partial
from typing import Any
from urllib import request

from .base import PostPayload, SocialConnector


class WebhookConnector(SocialConnector):
    """Posts serialized payloads to a webhook endpoint with bounded I/O."""

    def __init__(
        self,
        name: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        timeout_s: float = 10.0,
    ):
        super().__init__(name)
        if not endpoint or not endpoint.strip():
            raise ValueError("webhook endpoint must be a non-empty URL")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout_s = float(timeout_s)

    async def authenticate(self, **credentials: Any) -> None:
        await asyncio.sleep(0)
        token = credentials.get("token")
        if token:
            self.headers.setdefault("Authorization", f"Bearer {token}")

    def _publish_sync(self, req: request.Request) -> None:
        with request.urlopen(req, timeout=self.timeout_s) as response:
            response.read()

    async def publish(self, payload: PostPayload) -> None:
        body = json.dumps(
            {
                "headline": payload.copy.headline,
                "caption": payload.copy.caption,
                "hashtags": payload.copy.hashtags,
                "design": payload.design.to_dict(),
            }
        ).encode("utf-8")
        req = request.Request(self.endpoint, data=body, headers=self.headers)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(self._publish_sync, req))
