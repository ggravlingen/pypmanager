"""Market price."""
import pandas as pd


class MarketPrice:
    """Represent a security's market price."""

    def __init__(self) -> None:
        """Init class."""
        df = pd.read_csv("data/market_data.csv", sep=";")
        output_dict: dict[str, float] = {}
        for _, row in df.iterrows():
            output_dict[row.loc['isin_code']] = row.loc['price']

        self.lookup_table = output_dict
