"""Transaction loader for Lysa."""


from .base_loader import TransactionLoader


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
        df_raw = self.df_raw

        df_raw["commission"] = 0.0

        self.df_raw = df_raw
