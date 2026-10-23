"""Content generation utilities for social media posts."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

_PERSONA_TONE = {
    "general": ("friendly", "approachable"),
    "marketer": ("persuasive", "exciting"),
    "engineer": ("precise", "analytical"),
    "executive": ("visionary", "strategic"),
}


@dataclass
class PostCopy:
    """Container for generated copy."""

    headline: str
    caption: str
    hashtags: list[str]

    def render(self) -> str:
        tags = " ".join(f"#{tag}" for tag in self.hashtags)
        return f"{self.headline}\n\n{self.caption}\n\n{tags}".strip()


class ContentStrategy:
    """Represents a high-level approach for content generation."""

    def __init__(self, name: str, prompts: Iterable[str]):
        self.name = name
        self.prompts = tuple(prompts)

    def random_prompt(self) -> str:
        return random.choice(self.prompts)

    @staticmethod
    def from_name(name: str) -> "ContentStrategy":
        normalized = name.lower().strip()
        presets = {
            "educational": ContentStrategy(
                "educational",
                (
                    "Share a quick tutorial on {topic} in {tone} language.",
                    "Explain why {topic} matters for busy professionals.",
                    "Highlight a tip about {topic} that saves time.",
                ),
            ),
            "promotional": ContentStrategy(
                "promotional",
                (
                    "Announce a limited-time offer related to {topic} with urgency.",
                    "Promote a customer success story featuring {topic}.",
                    "Describe a feature tied to {topic} and invite action.",
                ),
            ),
            "announcement": ContentStrategy(
                "announcement",
                (
                    "Share breaking news about {topic} with excitement.",
                    "Reveal an upcoming event centered on {topic}.",
                    "Celebrate a milestone achieved through {topic}.",
                ),
            ),
        }
        return presets.get(normalized, presets["educational"])


class AutoWriter:
    """Generates social media copy from topic and persona inputs."""

    def __init__(self, strategy: ContentStrategy):
        self.strategy = strategy

    def _persona_tone(self, audience: str) -> str:
        values = _PERSONA_TONE.get(audience.lower(), _PERSONA_TONE["general"])
        return " and ".join(values)

    def _generate_hashtags(self, topic: str) -> list[str]:
        base = topic.replace(" ", "")
        extras = ["automation", "workflow", "productivity", "growth"]
        return [base.lower()] + random.sample(extras, k=2)

    def generate_post(self, topic: str, audience: str = "general") -> PostCopy:
        tone = self._persona_tone(audience)
        prompt = self.strategy.random_prompt().format(topic=topic, tone=tone)
        headline = prompt.split(".")[0].capitalize()
        caption = (
            f"{prompt} Published on {datetime.now(timezone.utc):%B %d, %Y}."
            " Encourage the reader to take the next step right away!"
        )
        hashtags = self._generate_hashtags(topic)
        return PostCopy(headline=headline, caption=caption, hashtags=hashtags)
