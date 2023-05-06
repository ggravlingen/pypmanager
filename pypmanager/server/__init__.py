"""Server."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from pypmanager.holding import Holding
from pypmanager.portfolio import Portfolio
from pypmanager.server.templates import load_template
from pypmanager.transaction_loader import load_data

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index(view: str | None = None) -> str:
    """Present overview page."""
    all_data, all_securities = load_data()

    holdings: list[Holding] = []
    for security_name in all_securities:
        holding = Holding(
            name=security_name,
            all_data=all_data,
        )

        if view is None and holding.current_holdings is None:
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
