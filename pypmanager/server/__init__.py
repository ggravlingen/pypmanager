"""Server."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from pypmanager.analytics import Portfolio
from pypmanager.helpers import (
    get_general_ledger_as_dict,
    get_historical_portfolio,
    get_holdings,
)
from pypmanager.server.graphql import graphql_app
from pypmanager.server.templates import load_template
from pypmanager.settings import Settings

app = FastAPI()


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Return favicon."""
    return FileResponse(f"{Settings.dir_static}/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """Present overview page."""
    holdings = await get_holdings()

    portfolio = Portfolio(holdings=holdings)

    return await load_template(
        template_name="current_portfolio.html",
        context={"securities": holdings, "portfolio": portfolio},
    )


@app.get("/ledger", response_class=HTMLResponse)
async def ledger() -> str:
    """Return the general ledger."""
    output_dict = get_general_ledger_as_dict()

    return await load_template(
        template_name="general_ledger.html",
        context={"ledger": output_dict},
    )


app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)


@app.get("/history", response_class=HTMLResponse)
async def portfolio_history() -> str:
    """Return historical data."""
    portfolio_data = await get_historical_portfolio()

    return await load_template(
        template_name="historical_portfolio.html",
        context={"data": portfolio_data},
    )


app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
