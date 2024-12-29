"""FastAPI server."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pypmanager.settings import Settings

from .graphql import graphql_app
from .scheduler import scheduler


@asynccontextmanager
async def async_lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Start and shutdown the scheduler."""
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=async_lifespan)

TypeGraphQL = Callable[[Request], Awaitable[Response] | Response]

app.add_route("/graphql", cast(TypeGraphQL, graphql_app))

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
