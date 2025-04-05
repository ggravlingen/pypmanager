"""Transaction loader for Lysa."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, cast

from pypmanager.helpers.security import async_security_map_name_to_isin

from .base_loader import TransactionLoader
from .const import (
    ColumnNameValues,
    CSVSeparator,
    CurrencyValues,
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)

_LOGGER = logging.getLogger(__package__)

if TYPE_CHECKING:
    import pandas as pd


def _replace_fee_name(row: pd.DataFrame) -> str:
    """Replace interest flows with cash and equivalemts."""
    if (
        row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE]
        == TransactionTypeValues.FEE.value
    ):
        return "Lysa management fee"

    return cast("str", row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY])


class LysaLoader(TransactionLoader):
    """Data loader for Lysa."""

    col_map = {  # noqa: RUF012
        "Date": TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE,
        "Type": TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE,
        "Amount": ColumnNameValues.AMOUNT,
        "Counterpart/Fund": TransactionRegistryColNameValues.SOURCE_NAME_SECURITY,
        "Volume": TransactionRegistryColNameValues.SOURCE_VOLUME,
        "Price": TransactionRegistryColNameValues.SOURCE_PRICE,
    }

    csv_separator = CSVSeparator.COMMA
    file_pattern = "lysa*.csv"
    date_format_pattern = "%Y-%m-%dT%H:%M:%S.%fZ"

    async def async_pre_process_df(self: LysaLoader) -> None:
        """Load CSV."""
        df_raw = self.df_final

        df_raw[TransactionRegistryColNameValues.SOURCE_BROKER.value] = "Lysa"
        df_raw[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY] = df_raw.apply(
            _replace_fee_name, axis=1
        )

        df_raw[TransactionRegistryColNameValues.SOURCE_FEE] = None
        df_raw[TransactionRegistryColNameValues.SOURCE_CURRENCY.value] = (
            CurrencyValues.SEK
        )

        # The exported CSV data contains special characters like � that we need to
        # replace
        with contextlib.suppress(AttributeError):
            df_raw[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY] = df_raw[
                TransactionRegistryColNameValues.SOURCE_NAME_SECURITY
            ].str.replace("�", "ä")

        security_map_name_to_isin = await async_security_map_name_to_isin()

        df_raw[TransactionRegistryColNameValues.SOURCE_ISIN.value] = df_raw[
            TransactionRegistryColNameValues.SOURCE_NAME_SECURITY
        ].map(security_map_name_to_isin)

        # Validate that ISIN exists for all relewant rows
        await self.async_validate_isin()

        self.df_final = df_raw

    async def async_validate_isin(self: LysaLoader) -> None:
        """Validate that an ISIN exists for all buy and sell transactions."""
        df_raw = self.df_final.copy()

        df_raw = df_raw.query(
            f"{TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value} in "
            f"['Buy', 'Sell']"
        )

        # Log an error if the name is not found in the dictionary
        missing_isin = df_raw[
            df_raw[TransactionRegistryColNameValues.SOURCE_ISIN.value].isna()
        ][TransactionRegistryColNameValues.SOURCE_NAME_SECURITY]

        for name in missing_isin:
            _LOGGER.error(f"ISIN code not found for security name: {name}")
