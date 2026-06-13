"""Base classes for social media connectors."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any

from ..content import PostCopy
from ..design import DesignTemplate


@dataclass
class PostPayload:
    """Normalized payload shared with connectors."""

    copy: PostCopy
    design: DesignTemplate


class SocialConnector(abc.ABC):
    """Interface for posting to a social network."""

    name: str

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    async def authenticate(self, **credentials: Any) -> None:
        """Authenticate using credentials."""

    @abc.abstractmethod
    async def publish(self, payload: PostPayload) -> None:
        """Publish a payload to the network."""
