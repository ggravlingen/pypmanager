"""Handle portfolios."""


from dataclasses import dataclass

from pypmanager.const import NUMBER_FORMATTER
from pypmanager.holding import Holding


@dataclass
class Portfolio:
    """Calculate portfolio value."""

    holdings: list[Holding]

    @property
    def mtm(self) -> float:
        """Return total market value."""
        return sum(s.market_value for s in self.holdings if s.market_value is not None)

    @property
    def invested_amount(self) -> float:
        """Return invested amount."""
        return sum(
            s.invested_amount for s in self.holdings if s.invested_amount is not None
        )

    @property
    def market_value(self) -> float:
        """Return market value of portfolio."""
        return sum(s.market_value for s in self.holdings if s.market_value is not None)

    @property
    def total_pnl(self) -> float:
        """Return total PnL."""
        return sum(s.total_pnl for s in self.holdings if s.total_pnl is not None)

    @property
    def realized_pnl(self) -> float:
        """Return realized PnL."""
        return sum(s.realized_pnl for s in self.holdings if s.realized_pnl is not None)

    @property
    def unrealized_pnl(self) -> float:
        """Return unrealized PnL."""
        return sum(
            s.unrealized_pnl for s in self.holdings if s.unrealized_pnl is not None
        )

    @property
    def dividends(self) -> float:
        """Return dividends."""
        return sum(s.dividends for s in self.holdings if s.dividends is not None)

    @property
    def total_transactions(self) -> int:
        """Return total number of transactions."""
        return sum(
            s.total_transactions
            for s in self.holdings
            if s.total_transactions is not None
        )

    @property
    def cli_table_row_total(self) -> list[str]:
        """Represent totals for CLI reports."""
        return [
            "Total",
            f"{self.invested_amount:{NUMBER_FORMATTER}}",
            f"{self.market_value:{NUMBER_FORMATTER}}",
            f"{self.total_pnl:{NUMBER_FORMATTER}}",
            f"{self.realized_pnl:{NUMBER_FORMATTER}}",
            f"{self.unrealized_pnl:{NUMBER_FORMATTER}}",
            "",
            f"{self.total_transactions}",
        ]
