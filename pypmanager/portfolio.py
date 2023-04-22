"""Handle portfolios."""


from dataclasses import dataclass
from pypmanager.security import Security


@dataclass
class Portfolio:
    """Calculate portfolio value."""

    securities: list[Security]

    def total_market_value(self, price: float) -> float:
        """Return total market value."""
        return sum(s.market_value(price) for s in self.securities)

    @property
    def total_cost_basis(self) -> float:
        """Return total cost basis."""
        return sum(s.cost_basis() for s in self.securities)

    def total_unrealized_pnl(self, price: float) -> float:
        """Return total unrealized PnL."""
        return sum(s.unrealized_pnl(price) for s in self.securities)
