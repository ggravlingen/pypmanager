"""Server."""
from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

from pypmanager.analytics import Portfolio
from pypmanager.analytics.holding import Holding
from pypmanager.loader_transaction import load_data
from pypmanager.server.templates import load_template
from pypmanager.settings import Settings

from .const import LOGGER

app = FastAPI()


@app.get("/favicon.ico")
async def get_favicon() -> FileResponse:
    """Return favicon."""
    return FileResponse(f"{Settings.DIR_STATIC}/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def index(view: str | None = None) -> str:
    """Present overview page."""
    all_data, all_securities = load_data()

    holdings: list[Holding] = []
    for security_name in all_securities:
        start_time = time.time()

        holding = Holding(
            name=security_name,
            all_data=all_data,
        )

        end_time = time.time()

        LOGGER.info(
            f"Calculated {security_name} in {round((end_time - start_time), 4)}s"
        )

        if view is None and holding.current_holdings is None:
            LOGGER.debug(f"Skipping {holding}")
            continue

        if view == "old" and holding.current_holdings is not None:
            continue

        holdings.append(holding)

    # Order by name
    holdings = sorted(holdings, key=lambda x: x.name)

    portfolio = Portfolio(holdings=holdings)

    return await load_template(
        template_name="current_portfolio.html",
        context={"securities": holdings, "portfolio": portfolio},
    )
