"""Output portfolio data in the command line."""

from prettytable import PrettyTable

from pypmanager.holding import Holding
from pypmanager.portfolio import Portfolio

TABLE_HEADER = [
    "Name",
    "Invested",
    "Market value",
    "PnL",
    "...realized",
    "...unrealized",
    "Value date",
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

        table.add_row(security_data.cli_table_row)

    portfolio = Portfolio(holdings=holdings)

    table.add_row(portfolio.cli_table_row_total)

    print(table)  # noqa: T201
