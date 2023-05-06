"""Transaction loader for Misc transactions."""


from .base_loader import TransactionLoader


class MiscLoader(TransactionLoader):
    """Data loader for misc data."""

    file_pattern = "other*.csv"

    def pre_process_df(self) -> None:
        """Load CSV."""
        self.rename_set_index_filter()
        df = self.df_raw

        self.df = df
