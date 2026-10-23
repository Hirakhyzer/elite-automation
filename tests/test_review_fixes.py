from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from elite_automation.content import PostCopy
from elite_automation.design import DesignTemplate
from elite_automation.poster import build_connector
from elite_automation.scheduler import Schedule, Scheduler
from elite_automation.connectors.webhook import WebhookConnector
from elite_automation.connectors.base import PostPayload


def _copy() -> PostCopy:
    return PostCopy(headline="h", caption="c", hashtags=["test"])


def _design() -> DesignTemplate:
    return DesignTemplate("#000", "#111", "#fff", "sans")


def test_webhook_config_requires_endpoint() -> None:
    with pytest.raises(ValueError, match="requires a non-empty 'endpoint'"):
        build_connector("prod", {"type": "webhook"})


def test_webhook_config_validates_timeout() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        build_connector("prod", {"type": "webhook", "endpoint": "https://example.test", "timeout_s": 0})


def test_webhook_passes_bounded_timeout_and_closes_response() -> None:
    connector = WebhookConnector("prod", "https://example.test", timeout_s=3.5)
    payload = PostPayload(copy=_copy(), design=_design())
    response = MagicMock()
    response.__enter__.return_value = response
    with patch("elite_automation.connectors.webhook.request.urlopen", return_value=response) as urlopen:
        asyncio.run(connector.publish(payload))
    assert urlopen.call_args.kwargs["timeout"] == 3.5
    response.read.assert_called_once_with()
    response.__exit__.assert_called_once()


def test_schedule_parse_normalizes_offset_to_utc() -> None:
    schedule = Schedule.parse("2026-01-01T12:00:00+02:00", _copy(), _design())
    assert schedule.run_at == datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)


def test_wait_until_chunks_long_delays() -> None:
    scheduler = Scheduler()
    future = datetime.now(timezone.utc) + timedelta(hours=2)

    async def exercise() -> None:
        with patch("elite_automation.scheduler.asyncio.sleep", new_callable=MagicMock) as sleep:
            async def cancel_after_first(delay: float) -> None:
                assert delay <= 300.0
                raise asyncio.CancelledError
            sleep.side_effect = cancel_after_first
            with pytest.raises(asyncio.CancelledError):
                await scheduler._wait_until(future)

    asyncio.run(exercise())
