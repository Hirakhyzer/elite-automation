"""Coordination layer for posting to multiple connectors."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from .content import PostCopy
from .design import DesignTemplate
from .connectors.base import PostPayload, SocialConnector
from .connectors.mock import MockConnector
from .connectors.webhook import WebhookConnector


_CONNECTOR_TYPES = {
    "mock": MockConnector,
    "webhook": WebhookConnector,
}


def build_connector(name: str, config: dict[str, Any]) -> SocialConnector:
    connector_type = config.get("type", "mock").lower()
    connector_cls = _CONNECTOR_TYPES.get(connector_type)
    if not connector_cls:
        raise ValueError(f"Unknown connector type: {connector_type}")
    if connector_cls is WebhookConnector:
        endpoint = config["endpoint"]
        headers = config.get("headers")
        return connector_cls(name=name, endpoint=endpoint, headers=headers)
    return connector_cls(name=name)


@dataclass
class AutoPoster:
    """Orchestrates posting to multiple connectors."""

    connectors: dict[str, SocialConnector]
    preview: bool = False

    async def post(self, copy: PostCopy, design: DesignTemplate) -> None:
        payload = PostPayload(copy=copy, design=design)
        coroutines = [self._send(connector, payload) for connector in self.connectors.values()]
        await asyncio.gather(*coroutines)

    async def _send(self, connector: SocialConnector, payload: PostPayload) -> None:
        if self.preview:
            print(f"[PREVIEW] {connector.name}: {payload.copy.render()}")
            return
        await connector.publish(payload)

    @classmethod
    async def create(cls, config: dict[str, Any], preview: bool = False) -> "AutoPoster":
        connectors: dict[str, SocialConnector] = {}
        configs = config.get("connectors", {"mock": {"type": "mock"}})
        for name, connector_config in configs.items():
            connector = build_connector(name, connector_config)
            credentials = connector_config.get("credentials", {})
            await connector.authenticate(**credentials)
            connectors[name] = connector
        if not connectors:
            connectors["mock"] = MockConnector(name="mock")
        return cls(connectors=connectors, preview=preview)
