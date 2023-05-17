"""Handle portfolios."""


from dataclasses import dataclass

from .holding import Holding


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
    def return_pct(self) -> float | None:
        """Return return in %."""
        if self.market_value and self.invested_amount:
            return self.market_value / self.invested_amount - 1

        return None

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
    def interest(self) -> float:
        """Return dividends."""
        return sum(s.interest for s in self.holdings if s.interest is not None)

    @property
    def total_transactions(self) -> int:
        """Return total number of transactions."""
        return sum(
            s.total_transactions
            for s in self.holdings
            if s.total_transactions is not None
        )
