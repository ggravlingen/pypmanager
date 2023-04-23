"""Output portfolio data in the command line."""

from prettytable import PrettyTable
from pypmanager.holding import Holding

from pypmanager.portfolio import Portfolio

NUMBER_FORMATTER = ",.0f"


def print_pretty_table(holdings: list[Holding]) -> None:
    """Print holdings."""
    sorted_holdings = sorted(holdings, key=lambda x: x.name)

    table = PrettyTable()
    table.field_names = [
        "Name",
        "Invested",
        "Holdings",
        "PnL",
        "...realized",
        "...unrealized",
    ]

    table.align["Name"] = "l"  # left align the "Name" column
    for field in [
        "Invested",
        "Holdings",
        "PnL",
        "...realized",
        "...unrealized",
    ]:
        table.align[field] = "r"

    for security_data in sorted_holdings:
        if security_data.current_holdings is None:
            continue

        table.add_row(
            [
                security_data.name,
                f"{security_data.invested_amount:{NUMBER_FORMATTER}}",
                f"{security_data.current_holdings:{NUMBER_FORMATTER}}",
                f"{security_data.total_pnl:{NUMBER_FORMATTER}}",
                f"{security_data.realized_pnl:{NUMBER_FORMATTER}}",
                f"{security_data.unrealized_pnl:{NUMBER_FORMATTER}}",
            ]
        )

    portfolio = Portfolio(holdings=holdings)

    table.add_row(
        [
            "Total",
            f"{portfolio.invested_amount:{NUMBER_FORMATTER}}",
            "",
            f"{portfolio.total_pnl:{NUMBER_FORMATTER}}",
            f"{portfolio.unrealized_pnl:{NUMBER_FORMATTER}}",
            f"{portfolio.realized_pnl:{NUMBER_FORMATTER}}",
        ]
    )

    print(table)
