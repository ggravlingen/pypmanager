"""Server."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from pypmanager.analytics import Portfolio
from pypmanager.helpers import get_general_ledger, get_holdings
from pypmanager.loader_transaction.const import ColumnNameValues
from pypmanager.server.graphql import graphql_app
from pypmanager.server.templates import load_template
from pypmanager.settings import Settings

app = FastAPI()


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Return favicon."""
    return FileResponse(f"{Settings.DIR_STATIC}/favicon.ico")


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
    df_general_ledger = get_general_ledger()
    df_general_ledger = df_general_ledger.sort_values(
        [
            ColumnNameValues.TRANSACTION_DATE,
            ColumnNameValues.NAME,
        ],
        ascending=False,
    )
    output_dict = df_general_ledger.reset_index().to_dict(orient="records")

    return await load_template(
        template_name="general_ledger.html",
        context={"ledger": output_dict},
    )


app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
