"""Helper functions."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

from pypmanager.ingest.transaction.const import (
    NUMBER_COLS,
    ColumnNameValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.settings import Settings

from .avanza import AvanzaLoader
from .generic import GenericLoader
from .lysa import LysaLoader
from .pandas_algorithm import PandasAlgorithm, PandasAlgorithmPnL

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime


DTYPES_MAP: dict[str, type[str | float] | str] = {
    # TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value is
    # handled in the class
    ColumnNameValues.ACCOUNT.value: str,
    TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value: str,
    TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value: str,
    TransactionRegistryColNameValues.SOURCE_VOLUME.value: float,
    TransactionRegistryColNameValues.SOURCE_PRICE.value: float,
    ColumnNameValues.AMOUNT.value: float,
    TransactionRegistryColNameValues.SOURCE_FEE.value: float,
    TransactionRegistryColNameValues.SOURCE_CURRENCY.value: str,
    TransactionRegistryColNameValues.SOURCE_ISIN.value: str,
    TransactionRegistryColNameValues.SOURCE_FX.value: float,
}

FILTER_STATEMENT = (
    f"('{TransactionTypeValues.DIVIDEND}'"
    f",'{TransactionTypeValues.FEE}'"
    f",'{TransactionTypeValues.FEE_CREDIT}'"
    f",'{TransactionTypeValues.INTEREST}'"
    f",'{TransactionTypeValues.DEPOSIT}'"
    f",'{TransactionTypeValues.CASHBACK}'"
    f",'{TransactionTypeValues.WITHDRAW}'"
    f",'{TransactionTypeValues.TAX}'"
    f",'{TransactionTypeValues.BUY}'"
    f",'{TransactionTypeValues.SELL}',)"
)


@dataclass
class ReplaceConfig:
    """Configuration to replace values."""

    search: list[str]
    target: str


REPLACE_CONFIG = [
    ReplaceConfig(
        search=["Köp", "Switch buy", "Buy"],
        target=TransactionTypeValues.BUY.value,
    ),
    ReplaceConfig(
        search=["Sälj", "Switch sell", "Sell"],
        target=TransactionTypeValues.SELL.value,
    ),
    ReplaceConfig(
        search=["Räntor"],
        target=TransactionTypeValues.INTEREST.value,
    ),
    ReplaceConfig(
        search=["Preliminärskatt"],
        target=TransactionTypeValues.TAX.value,
    ),
    ReplaceConfig(
        search=["Utdelning"],
        target=TransactionTypeValues.DIVIDEND.value,
    ),
    ReplaceConfig(
        search=["Fee", "Plattformsavgift"],
        target=TransactionTypeValues.FEE.value,
    ),
    ReplaceConfig(
        search=["Deposit", "Insättning"],
        target=TransactionTypeValues.DEPOSIT.value,
    ),
]


@dataclass
class ColumnAppendConfig:
    """Configuration to append columns."""

    column: str
    callable: Callable[[pd.DataFrame], pd.DataFrame]


# These columns are appended to the transaction registry
COLUMN_APPEND: tuple[ColumnAppendConfig, ...] = (
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.CALC_TURNOVER_OR_OTHER_CF.value,
        callable=PandasAlgorithm.turnover_or_other_cash_flow,
    ),
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.CASH_FLOW_NET_FEE_NOMINAL.value,
        callable=PandasAlgorithm.calculate_cash_flow_net_fee_nominal,
    ),
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.CASH_FLOW_GROSS_FEE_NOMINAL.value,
        callable=PandasAlgorithm.calculate_cash_flow_gross_fee_nominal,
    ),
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value,
        callable=PandasAlgorithmPnL.calculate_pnl_dividend,
    ),
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.CALC_PNL_TRADE.value,
        callable=PandasAlgorithmPnL.calculate_pnl_trade,
    ),
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.CALC_PNL_TOTAL.value,
        callable=PandasAlgorithmPnL.calculate_pnl_total,
    ),
)

COLUMN_CLEANUP: tuple[ColumnAppendConfig, ...] = (
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.PRICE_PER_UNIT.value,
        callable=PandasAlgorithm.cleanup_price_per_unit,
    ),
    ColumnAppendConfig(
        column=TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value,
        callable=PandasAlgorithm.cleanup_quantity_held,
    ),
)


class TransactionRegistry:
    """
    Create a normalised registry for all transactions.

    This registry is the basis for all other calculations.
    """

    def __init__(
        self: TransactionRegistry,
        report_date: datetime | None = None,
        *,
        sort_by_date_descending: bool = False,
    ) -> None:
        """Init class."""
        if report_date is not None and (
            report_date.tzinfo is None
            or report_date.tzinfo.utcoffset(report_date) is None
        ):
            msg = "report_date argument must be time zone aware"
            raise ValueError(msg)

        self.report_date = report_date
        self.sort_by_date_descending = sort_by_date_descending

        # Load all transaction files into a dataframe
        self.df_all_transactions = self._load_transaction_files()

        # Cleanup must be done before converting data types
        self._100_cleanup_df()

        # Run the first sequence of normalisation
        self._200_normalize_and_filter_transaction_type()
        self._201_normalise_transaction_date()
        self._202_normalize_data()
        self._203_convert_data_types()

        # There are no transactions to process so we can return
        if self.df_all_transactions.empty:
            return

        self._300_calculate_average_price()

        # Set index
        self._400_set_index()

        # Append columns containing derived meta data
        self._500_append_columns()

        # Cleanup data that we don't need in the final result
        self._600_final_cleanup()

        # Set index and, sort by transaction date and filter by date, if applicable
        self._sort_transactions()
        self._filter_by_date()

        # Validate columns
        self._validate_columns()

    def _load_transaction_files(self: TransactionRegistry) -> pd.DataFrame:
        """Load transaction files and return a sorted DataFrame."""
        df_generic = GenericLoader().df_final
        df_avanza = AvanzaLoader().df_final
        df_lysa = LysaLoader().df_final

        return pd.concat([df_generic, df_avanza, df_lysa])

    def _100_cleanup_df(self: TransactionRegistry) -> None:
        """Cleanup dataframe."""
        df_raw = self.df_all_transactions.copy()

        # Ensure all number columns are floats
        for col in NUMBER_COLS:
            if col in df_raw.columns:
                df_raw[col] = df_raw.apply(
                    lambda x, _col=col: PandasAlgorithm.cleanup_number(x[_col]),
                    axis=1,
                )

        # Replace dashes with 0
        for col in (
            TransactionRegistryColNameValues.SOURCE_FEE,
            TransactionRegistryColNameValues.SOURCE_ISIN,
        ):
            if col in df_raw.columns:
                with contextlib.suppress(AttributeError):
                    df_raw[col] = df_raw[col].str.replace("-", "").replace("", 0)

        self.df_all_transactions = df_raw

    def _200_normalize_and_filter_transaction_type(self: TransactionRegistry) -> None:
        """
        Normalize transaction types.

        In the source data, transactions will be named differently. To enable
        calculations, we replace the names in the source data with our internal names.
        """
        df_raw = self.df_all_transactions.copy()

        for config in REPLACE_CONFIG:
            for event in config.search:
                df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE] = (
                    df_raw[
                        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE
                    ].replace(event, config.target)
                )

        df_raw = df_raw.query(
            f"{TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE} in "
            f"{FILTER_STATEMENT}",
        )

        self.df_all_transactions = df_raw

    def _201_normalise_transaction_date(self: TransactionRegistry) -> None:
        """Make transaction date aware using system time zone."""
        df_raw = self.df_all_transactions.copy()

        # Convert all datetime objects to UTC
        df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value] = (
            df_raw[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value]
            .dt.tz_localize(None)
            .dt.tz_localize(Settings.system_time_zone)
        )

        self.df_all_transactions = df_raw

    def _202_normalize_data(self: TransactionRegistry) -> None:
        """Make sure data is calculated in the same way."""
        df_raw = self.df_all_transactions.copy()

        df_raw[TransactionRegistryColNameValues.SOURCE_VOLUME.value] = df_raw.apply(
            PandasAlgorithm.normalize_no_traded, axis=1
        )
        df_raw[ColumnNameValues.AMOUNT.value] = df_raw.apply(
            PandasAlgorithm.normalize_amount, axis=1
        )
        df_raw[TransactionRegistryColNameValues.SOURCE_FX.value] = df_raw.apply(
            PandasAlgorithm.normalize_fx, axis=1
        )

        self.df_all_transactions = df_raw

    def _203_convert_data_types(self: TransactionRegistry) -> None:
        """Convert columns to correct data types."""
        df_raw = self.df_all_transactions.copy()
        for key, val in DTYPES_MAP.items():
            if key in df_raw.columns:
                try:
                    df_raw[key] = df_raw[key].astype(val)
                except ValueError as err:
                    msg = f"Unable to parse {key}"
                    raise ValueError(msg) from err

        self.df_all_transactions = df_raw

    def _filter_by_date(self: TransactionRegistry) -> None:
        """Filter transactions by date."""
        df_raw = self.df_all_transactions.copy()

        if self.report_date is not None:
            df_raw = df_raw.query(f"index <= '{self.report_date}'")

        self.df_all_transactions = df_raw

    def _300_calculate_average_price(self: TransactionRegistry) -> None:
        """Calculate average price."""
        df_raw = self.df_all_transactions.copy()

        df_sorted = df_raw.sort_values(
            by=[
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value,
            ],
            ascending=[True, True, True],
        )

        df_sorted[ColumnNameValues.AMOUNT.value] = (
            df_sorted[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
            * df_sorted[TransactionRegistryColNameValues.SOURCE_PRICE.value]
        )
        df_sorted[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value] = (
            df_sorted.apply(
                lambda x: (
                    (
                        x[
                            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value
                        ]
                        == TransactionTypeValues.BUY.value
                    )
                    - (
                        x[
                            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value
                        ]
                        == TransactionTypeValues.SELL.value
                    )
                )
                # Make sure traded volume is always a positive integer
                * abs(x[TransactionRegistryColNameValues.SOURCE_VOLUME.value]),
                axis=1,
            )
        )
        df_sorted[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value] = (
            df_sorted.groupby(
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value
            )[TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value].cumsum()
        )

        df_sorted = (
            df_sorted.groupby(
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value
            )
            .apply(
                PandasAlgorithm.calculate_adjusted_price_per_unit, include_groups=False
            )
            # Add bane back as a column
            .reset_index(drop=False)
        )

        # Drop the column that is appended in the group by above
        df_sorted = df_sorted.drop(
            columns=[
                "level_1",
                TransactionRegistryColNameValues.INTERNAL_TURNOVER.value,
            ]
        )

        self.df_all_transactions = df_sorted

    def _400_set_index(self: TransactionRegistry) -> None:
        """Set index."""
        df_raw = self.df_all_transactions.copy()

        df_raw = df_raw.set_index(
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value
        )

        self.df_all_transactions = df_raw

    def _500_append_columns(self: TransactionRegistry) -> None:
        """Append calculated columns."""
        df_raw = self.df_all_transactions.copy()

        for config in COLUMN_APPEND:
            df_raw[config.column] = df_raw.apply(config.callable, axis=1)

        # Add transaction year
        df_raw[TransactionRegistryColNameValues.META_TRANSACTION_YEAR.value] = (
            df_raw.index.year
        )

        self.df_all_transactions = df_raw

    def _600_final_cleanup(self: TransactionRegistry) -> None:
        """
        Cleanup data.

        This removes data we don't need in the final result.
        """
        df_raw = self.df_all_transactions.copy()

        for config in COLUMN_CLEANUP:
            df_raw[config.column] = df_raw.apply(config.callable, axis=1)

        self.df_all_transactions = df_raw

    def _sort_transactions(self: TransactionRegistry) -> None:
        """Sort transactions."""
        df_raw = self.df_all_transactions.copy()

        if self.sort_by_date_descending:
            df_raw = df_raw.sort_index(ascending=False)
        else:
            df_raw = df_raw.sort_index()

        self.df_all_transactions = df_raw

    def _validate_columns(self: TransactionRegistry) -> None:
        """Validate columns."""
        expected_columns = [
            "source_name",
            "source_transaction_type",
            "source_isin_code",
            "source_volume",
            "source_price",
            "amount",
            "source_fee",
            "source_currency",
            "source_broker",
            "source_file_name",
            "source_fx_rate",
            "source_account_name",
            "calc_agg_sum_quantity_held",
            "calc_avg_price_per_unit",
            "calc_turnover_or_cash_flow",
            "calc_cf_net_fee_nominal_ccy",
            "calc_cf_gross_fee_nominal_ccy",
            "calc_pnl_transaction_dividend",
            "calc_pnl_transaction_trade",
            "calc_pnl_transaction_total",
            "meta_transaction_year",
        ]

        actual_columns = self.df_all_transactions.columns.tolist()

        # Find columns that are in actual_columns but not in expected_columns
        missing_columns = set(expected_columns) - set(actual_columns)
        extra_columns = set(actual_columns) - set(expected_columns)

        if missing_columns:
            msg = (
                f"Columns are not as expected. Missing columns: {missing_columns}. "
                f"Extra columns: {extra_columns}"
            )
            raise ValueError(msg)

    async def async_get_registry(self) -> pd.DataFrame:
        """Get registry."""
        return self.df_all_transactions
