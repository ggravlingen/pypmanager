"""Main scheduler app."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, JobExecutionEvent
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pypmanager.helpers.market_data import async_download_market_data
from pypmanager.settings import Settings

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

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


async def run_main() -> None:
    """Run main script."""
    LOGGER.info("Started scheduler")
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
        trigger="cron",
        hour=21,
        minute=0,
        replace_existing=True,
    )

    scheduler.start()

    await asyncio.sleep(1)  # Sleep for a short while to allow scheduler to start
    scheduler.print_jobs()

    # Keep the script running indefinitely
    while True:
        await DONE.wait()


if __name__ == "__main__":
    asyncio.run(run_main())
