"""Configure a scheduler."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pypmanager.database.helpers import sync_security_files_to_db
from pypmanager.helpers.market_data import async_download_market_data
from pypmanager.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

LOGGER = logging.getLogger(__name__)


DONE = asyncio.Event()


def event_listener(event: JobExecutionEvent) -> None:
    """Handle events coming from the event loop."""
    if event.exception:
        LOGGER.warning(f"Error running {event.job_id}", exc_info=event.exception)


async def run_async_job(
    job_func: Callable[..., Coroutine[Any, Any, None]],
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> None:
    """Run an async job function."""
    await job_func(*args, **kwargs)


scheduler = AsyncIOScheduler(
    executors={
        "threadpool": ThreadPoolExecutor(max_workers=1),
    },
    timezone=Settings.system_time_zone,
)
scheduler.add_listener(event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

scheduler.add_job(
    run_async_job,
    id="load_market_data",
    args=[async_download_market_data],
    # Run every four hours
    trigger="interval",
    hours=4,
    replace_existing=True,
)
scheduler.add_job(
    run_async_job,
    id="sync_security_files_to_db",
    args=[sync_security_files_to_db],
    # Run every four hours
    trigger="interval",
    hours=1,
    replace_existing=True,
)
