"""Market price."""
import csv
from dataclasses import dataclass


@dataclass
class MarketPrice:
    """Represent a security's market price."""

    symbol: str
    price: float

    @classmethod
    def from_csv(cls, filename, symbol):
        """Load value from csv file."""
        with open(filename, encoding="UTF-8") as _f:
            reader = csv.DictReader(_f)
            for row in reader:
                if row["Symbol"] == symbol:
                    return cls(symbol, float(row["Price"]))

        raise ValueError(f"No data found for symbol {symbol}")
