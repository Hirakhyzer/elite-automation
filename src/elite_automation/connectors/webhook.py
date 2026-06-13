"""Webhook-based connector implementation."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib import request

from .base import PostPayload, SocialConnector


class WebhookConnector(SocialConnector):
    """Posts serialized payloads to a webhook endpoint."""

    def __init__(self, name: str, endpoint: str, headers: dict[str, str] | None = None):
        super().__init__(name)
        self.endpoint = endpoint
        self.headers = headers or {"Content-Type": "application/json"}

    async def authenticate(self, **credentials: Any) -> None:
        await asyncio.sleep(0)
        token = credentials.get("token")
        if token:
            self.headers.setdefault("Authorization", f"Bearer {token}")

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
        await loop.run_in_executor(None, request.urlopen, req)
