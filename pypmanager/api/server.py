"""FastAPI server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pypmanager.settings import Settings

from .graphql import graphql_app

app = FastAPI()

TypeGraphQL = Callable[[Request], Awaitable[Response] | Response]

app.add_route("/graphql", cast(TypeGraphQL, graphql_app))

app.mount("/static", StaticFiles(directory=Settings.dir_static), name="static")


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Return favicon."""
    return FileResponse(f"{Settings.dir_static}/favicon.ico")


@app.get("/", response_class=FileResponse)
async def index_page() -> FileResponse:
    """Return the index page."""
    return FileResponse(f"{Settings.dir_templates}/index.html")
