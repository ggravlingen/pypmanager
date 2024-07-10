"""Server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pypmanager.analytics import Portfolio
from pypmanager.helpers import (
    get_historical_portfolio,
    get_holdings,
)
from pypmanager.server.graphql import graphql_app
from pypmanager.server.templates import load_template
from pypmanager.settings import Settings

app = FastAPI()

TypeGraphQL = Callable[[Request], Awaitable[Response] | Response]

app.add_route("/graphql", cast(TypeGraphQL, graphql_app))

app.mount("/static", StaticFiles(directory=Settings.dir_static), name="static")


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Return favicon."""
    return FileResponse(f"{Settings.dir_static}/favicon.ico")


@app.get("/portfolio", response_class=HTMLResponse)
async def index() -> str:
    """Present overview page."""
    holdings = await get_holdings()

    portfolio = Portfolio(holdings=holdings)

    return await load_template(
        template_name="current_portfolio.html",
        context={"securities": holdings, "portfolio": portfolio},
    )


@app.get("/history", response_class=HTMLResponse)
async def portfolio_history() -> str:
    """Return historical data."""
    portfolio_data = await get_historical_portfolio()

    return await load_template(
        template_name="historical_portfolio.html",
        context={"data": portfolio_data},
    )


@app.get("/", response_class=FileResponse)
async def react_page() -> FileResponse:
    """Return historical data."""
    return FileResponse(f"{Settings.dir_templates}/app.html")
