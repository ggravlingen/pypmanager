"""Tests for api.scheduler module."""

from __future__ import annotations

from apscheduler.events import JobExecutionEvent
import pytest

from pypmanager.api.scheduler import event_listener, run_async_job


def test_event_listener(caplog: pytest.LogCaptureFixture) -> None:
    """Test event_listener function."""
    event = JobExecutionEvent(
        job_id="test_job_id",
        jobstore="test_jobstore",
        scheduled_run_time=0,
        code="abc",
    )
    event.exception = Exception("Test exception")
    event_listener(event)
    assert "Error running test_job_id" in caplog.text


@pytest.mark.asyncio
async def test_run_async_job() -> None:
    """Test run_async_job function."""

    async def async_job() -> None:
        pass

    await run_async_job(async_job)
    assert True
