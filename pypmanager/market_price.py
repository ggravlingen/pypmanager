"""Market price."""
import pandas as pd


class MarketPrice:
    """Represent a security's market price."""

    def __init__(self) -> None:
        """Init class."""
        df = pd.read_csv("data/market_data.csv", sep=";")
        output_dict: dict[str, float] = {}
        for _, row in df.iterrows():
            if row.loc['isin_code'] not in output_dict:
                output_dict[row.loc['isin_code']] = {}

            output_dict[row.loc['isin_code']] = {
                "price": row.loc['price'],
                "report_date": row.loc['report_date'],
            }

        self.lookup_table = output_dict
