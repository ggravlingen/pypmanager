"""Transaction loader for Lysa."""


from .base_loader import TransactionLoader
from .const import TransactionTypeValues


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

    col_map = {
        "Date": "transaction_date",
        "Type": "transaction_type",
        "Amount": "amount",
        "Counterpart/Fund": "name",
        "Volume": "no_traded",
        "Price": "price",
    }

    csv_separator = ","
    file_pattern = "lysa*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        df = self.df_raw

        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Replace buy
        for event in ("Switch buy", "Buy"):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.BUY.value
            )

        # Replace sell
        for event in ("Switch sell", "Sell"):
            df["transaction_type"] = df["transaction_type"].replace(
                event, TransactionTypeValues.SELL.value
            )

        df["commission"] = 0.0

        self.df_raw = df
