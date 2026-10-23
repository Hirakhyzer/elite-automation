"""Design generation for social media assets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # Optional Pillow support
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
except ImportError:  # pragma: no cover - pillow not installed
    Image = ImageDraw = ImageFont = None  # type: ignore


@dataclass
class DesignTemplate:
    """Description of a generated design."""

    background_color: str
    accent_color: str
    text_color: str
    typography: str
    output_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "background_color": self.background_color,
            "accent_color": self.accent_color,
            "text_color": self.text_color,
            "typography": self.typography,
            "output_path": str(self.output_path) if self.output_path else None,
        }


class AutoDesigner:
    """Creates lightweight visual assets for social posts."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("designs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _palette_for_topic(self, topic: str) -> tuple[str, str]:
        normalized = topic.lower()
        if "ai" in normalized or "automation" in normalized:
            return "#0F172A", "#38BDF8"
        if "marketing" in normalized:
            return "#1E293B", "#F97316"
        return "#111827", "#22C55E"

    def _ensure_font(self) -> Any | None:
        if ImageFont is None:  # Pillow missing
            return None
        try:
            return ImageFont.truetype("DejaVuSans.ttf", 64)
        except OSError:
            return ImageFont.load_default()

    def _render_image(self, message: str, background: str, accent: str) -> Path | None:
        if Image is None:
            return None
        width, height = 1200, 1200
        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)
        font = self._ensure_font()
        text_color = "#F8FAFC"
        text_box = (80, 80, width - 80, height - 80)
        draw.rectangle([(60, height - 220), (width - 60, height - 120)], fill=accent)
        draw.text((120, 920), "elite automation", fill="white", font=font)
        draw.text((text_box[0], text_box[1]), message[:100], fill=text_color, font=font)
        output_path = self.output_dir / f"post-{abs(hash(message)) % 10_000}.png"
        image.save(output_path)
        return output_path

    def create_design(self, topic: str, message: str) -> DesignTemplate:
        background, accent = self._palette_for_topic(topic)
        typography = "Sans-serif Bold"
        output = self._render_image(message=message, background=background, accent=accent)
        text_color = "#F8FAFC"
        return DesignTemplate(
            background_color=background,
            accent_color=accent,
            text_color=text_color,
            typography=typography,
            output_path=output,
        )
