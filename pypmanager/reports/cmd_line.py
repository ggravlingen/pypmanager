"""Output portfolio data in the command line."""

from prettytable import PrettyTable
from pypmanager.holding import Holding

from pypmanager.portfolio import Portfolio

NUMBER_FORMATTER = ",.0f"

TABLE_HEADER = [
    "Name",
    "Invested",
    "Holdings",
    "Current price",
    "Value date",
    "PnL",
    "...realized",
    "...unrealized",
    "# trades",
]


def print_pretty_table(holdings: list[Holding]) -> None:
    """Print holdings."""
    sorted_holdings = sorted(holdings, key=lambda x: x.name)

    table = PrettyTable()
    table.field_names = TABLE_HEADER

    for field in TABLE_HEADER:
        table.align[field] = "r"

    # Overwrite default
    table.align["Name"] = "l"

    for security_data in sorted_holdings:
        if security_data.current_holdings is None:
            continue

        table.add_row(
            [
                security_data.name,
                f"{security_data.invested_amount:{NUMBER_FORMATTER}}",
                f"{security_data.current_holdings:{NUMBER_FORMATTER}}",
                f"{security_data.current_price}",
                f"{security_data.date_market_value}",
                f"{security_data.total_pnl:{NUMBER_FORMATTER}}",
                f"{security_data.realized_pnl:{NUMBER_FORMATTER}}",
                f"{security_data.unrealized_pnl:{NUMBER_FORMATTER}}",
                f"{security_data.total_transactions}",
            ],
        )

    portfolio = Portfolio(holdings=holdings)

    table.add_row(
        [
            "Total",
            f"{portfolio.invested_amount:{NUMBER_FORMATTER}}",
            "",
            "",
            "",
            f"{portfolio.total_pnl:{NUMBER_FORMATTER}}",
            f"{portfolio.unrealized_pnl:{NUMBER_FORMATTER}}",
            f"{portfolio.realized_pnl:{NUMBER_FORMATTER}}",
            "",
        ],
    )

    print(table)
