"""FastAPI server."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
import logging
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pypmanager.database.helpers import sync_security_files_to_db
from pypmanager.settings import (
    APP_DATA,
    APP_FRONTEND,
    APP_ROOT,
    Settings,
)

from .graphql import graphql_app
from .scheduler import scheduler

_LOGGER = logging.getLogger("pypmanager.startup")


@asynccontextmanager
async def async_lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Start and shutdown the scheduler."""
    for folder, name in [
        (APP_ROOT, "App folder"),
        (APP_DATA, "User data folder"),
        (APP_FRONTEND, "Frontend folder"),
        (Settings.dir_configuration_local, "Configuration folder"),
        (Settings.dir_transaction_data_local, "Transactions folder"),
    ]:
        if folder.exists():
            _LOGGER.info(f"{name} exists at {folder}")
        else:
            _LOGGER.info(f"{name} is missing at {folder}")

    _LOGGER.info(f"Database file: {Settings.database_local}")

    scheduler.start()
    await sync_security_files_to_db()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=async_lifespan)

TypeGraphQL = Callable[[Request], Awaitable[Response] | Response]

app.add_route("/graphql", cast("TypeGraphQL", graphql_app))

app.mount("/static", StaticFiles(directory=Settings.dir_static), name="static")


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Return favicon."""
    return FileResponse(f"{Settings.dir_static}/favicon.ico")


@app.get("/status")
def get_index() -> HTMLResponse:
    """Return status OK."""
    return HTMLResponse(content="OK")


@app.get("/", response_class=FileResponse)
async def index_page() -> FileResponse:
    """Return the index page."""
    return FileResponse(f"{Settings.dir_templates}/index.html")
