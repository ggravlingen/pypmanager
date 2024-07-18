"""Helper functions."""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import pandas as pd

from pypmanager.ingest.transaction.const import (
    NUMBER_COLS,
    ColumnNameValues,
    TransactionTypeValues,
)
from pypmanager.settings import Settings

from .avanza import AvanzaLoader
from .generic import GenericLoader
from .lysa import LysaLoader
from .pandas_algorithm import PandasAlgorithm

if TYPE_CHECKING:
    from datetime import datetime


DTYPES_MAP: dict[str, type[str | float] | str] = {
    # ColumnNameValues.TRANSACTION_DATE.value is handled in the class
    ColumnNameValues.ACCOUNT.value: str,
    ColumnNameValues.TRANSACTION_TYPE.value: str,
    ColumnNameValues.NAME.value: str,
    ColumnNameValues.NO_TRADED.value: float,
    ColumnNameValues.PRICE.value: float,
    ColumnNameValues.AMOUNT.value: float,
    ColumnNameValues.COMMISSION.value: float,
    ColumnNameValues.CURRENCY.value: str,
    ColumnNameValues.ISIN_CODE.value: str,
    ColumnNameValues.FX.value: float,
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


def _normalize_amount(row: pd.DataFrame) -> float:
    """Calculate amount if nan."""
    if row[ColumnNameValues.TRANSACTION_TYPE] in [
        TransactionTypeValues.CASHBACK,
        TransactionTypeValues.FEE,
    ]:
        amount = row[ColumnNameValues.AMOUNT]
    else:
        amount = row[ColumnNameValues.NO_TRADED] * row[ColumnNameValues.PRICE]

    # Buy and tax is a negative cash flow for us
    if row[ColumnNameValues.TRANSACTION_TYPE] in [
        TransactionTypeValues.BUY,
        TransactionTypeValues.TAX,
        TransactionTypeValues.FEE,
    ]:
        amount = abs(amount) * -1
    else:
        amount = abs(amount)

    return cast(float, amount)


def _calculate_cash_flow_nominal(row: pd.DataFrame) -> float:
    """Calculate cash flow."""
    if (amount := cast(float | None, row[ColumnNameValues.AMOUNT.value])) is None:
        return 0.0

    if row[ColumnNameValues.COMMISSION.value] is None:
        commission = 0.0
    else:
        commission = cast(float, row[ColumnNameValues.COMMISSION.value])

    return amount + commission


def _cleanup_number(value: str | None) -> float | None:
    """Make sure values are converted to floats."""
    if value is None:
        return None

    if (value := f"{value}") == "-":
        return 0

    value = value.replace(",", ".")
    value = value.replace(" ", "")

    try:
        return float(value)
    except ValueError as err:
        msg = f"Unable to parse {value}"
        raise ValueError(msg) from err


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
        self.report_date = report_date
        self.sort_by_date_descending = sort_by_date_descending

        self.df_all_transactions = self._load_transaction_files()

        self._normalise_transaction_date()
        self._set_index()
        self._normalize_transaction_type()
        # Cleanup must be done before converting data types
        self._cleanup_df()
        self._convert_data_types()
        self._filter_transactions()
        self._normalize_data()
        self._sort_transactions()

    def _load_transaction_files(self: TransactionRegistry) -> pd.DataFrame:
        """Load transaction files and return a sorted DataFrame."""
        df_generic = GenericLoader(self.report_date).df_final
        df_avanza = AvanzaLoader(self.report_date).df_final
        df_lysa = LysaLoader(self.report_date).df_final

        return pd.concat([df_generic, df_avanza, df_lysa])

    def _normalise_transaction_date(self: TransactionRegistry) -> None:
        """Make transaction date aware using system time zone."""
        df_raw = self.df_all_transactions.copy()

        # Convert all datetime objects to UTC
        df_raw[ColumnNameValues.TRANSACTION_DATE.value] = (
            df_raw[ColumnNameValues.TRANSACTION_DATE.value]
            .dt.tz_localize(None)
            .dt.tz_localize(Settings.system_time_zone)
        )

        self.df_all_transactions = df_raw

    def _convert_data_types(self: TransactionRegistry) -> None:
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

    def _set_index(self: TransactionRegistry) -> None:
        """Set index."""
        df_raw = self.df_all_transactions.copy()

        df_raw = df_raw.set_index(ColumnNameValues.TRANSACTION_DATE.value)

        self.df_all_transactions = df_raw

    def _normalize_transaction_type(self: TransactionRegistry) -> None:
        """
        Normalize transaction types.

        In the source data, transactions will be named differently. To enable
        calculations, we replace the names in the source data with our internal names.
        """
        df_raw = self.df_all_transactions.copy()

        for config in REPLACE_CONFIG:
            for event in config.search:
                df_raw[ColumnNameValues.TRANSACTION_TYPE] = df_raw[
                    ColumnNameValues.TRANSACTION_TYPE
                ].replace(event, config.target)
        self.df_all_transactions = df_raw

    def _filter_transactions(self: TransactionRegistry) -> None:
        """Remove transactions we are not able to process."""
        df_raw = self.df_all_transactions.copy()
        df_raw = df_raw.query(
            f"{ColumnNameValues.TRANSACTION_TYPE} in {FILTER_STATEMENT}",
        )
        self.df_all_transactions = df_raw

    def _cleanup_df(self: TransactionRegistry) -> None:
        """Cleanup dataframe."""
        df_raw = self.df_all_transactions.copy()

        # Ensure all number columns are floats
        for col in NUMBER_COLS:
            if col in df_raw.columns:
                df_raw[col] = df_raw.apply(
                    lambda x, _col=col: _cleanup_number(x[_col]),
                    axis=1,
                )

        # Replace dashes with 0
        for col in (
            ColumnNameValues.COMMISSION,
            ColumnNameValues.ISIN_CODE,
        ):
            if col in df_raw.columns:
                with contextlib.suppress(AttributeError):
                    df_raw[col] = df_raw[col].str.replace("-", "").replace("", 0)

        self.df_all_transactions = df_raw

    def _normalize_data(self: TransactionRegistry) -> None:
        """Make sure data is calculated in the same way."""
        df_raw = self.df_all_transactions.copy()

        df_raw[ColumnNameValues.NO_TRADED.value] = df_raw.apply(
            PandasAlgorithm.normalize_no_traded, axis=1
        )
        df_raw[ColumnNameValues.AMOUNT.value] = df_raw.apply(_normalize_amount, axis=1)
        df_raw[ColumnNameValues.FX.value] = df_raw.apply(
            PandasAlgorithm.normalize_fx, axis=1
        )
        df_raw[ColumnNameValues.CASH_CLOW_NOMAL.value] = df_raw.apply(
            _calculate_cash_flow_nominal, axis=1
        )

        self.df_all_transactions = df_raw

    def _sort_transactions(self: TransactionRegistry) -> None:
        """Sort transactions."""
        df_raw = self.df_all_transactions.copy()

        if self.sort_by_date_descending:
            df_raw = df_raw.sort_index(ascending=False)
        else:
            df_raw = df_raw.sort_index()

        self.df_all_transactions = df_raw

    async def async_get_registry(self) -> pd.DataFrame:
        """Get registry."""
        return self.df_all_transactions
