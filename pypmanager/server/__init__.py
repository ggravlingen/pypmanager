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
async def all_checks() -> str:
    """Present overview page."""
    all_data, all_securities = load_data()

    calc_security_list: list[Holding] = []
    for security_name in all_securities:
        calc_security_list.append(
            Holding(
                name=security_name,
                all_data=all_data,
            )
        )

    portfolio = Portfolio(holdings=calc_security_list)

    return await load_template(
        template_name="current_portfolio.html",
        context={"securities": calc_security_list, "portfolio": portfolio},
    )
