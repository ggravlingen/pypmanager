"""Chart helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003

import numpy as np
import pandas as pd
import strawberry

from pypmanager.helpers.market_data import async_get_market_data
from pypmanager.helpers.security_holding_history import SecurityHoldingHistory
from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.utils.dt import (
    async_filter_df_by_date_range,
    async_get_empty_df_with_datetime_index,
)


@strawberry.type
@dataclass
class ChartData:
    """Define chart data."""

    x_val: date
    y_val: float | None

    volume_buy: float | None
    volume_sell: float | None
    dividend_per_security: float | None

    cost_price_average: float | None = None

    @property
    def is_buy(self) -> bool:
        """Return if buy."""
        return bool(self.volume_buy and self.volume_buy > 0)

    @property
    def is_sell(self) -> bool:
        """Return if sell."""
        return bool(self.volume_sell and self.volume_sell > 0)


async def async_get_market_data_and_transaction(
    isin_code: str,
    *,
    start_date: date,
    end_date: date,
) -> list[ChartData]:
    """Create chart data for historical price development and buy/sell."""
    output_data: list[ChartData] = []

    # These are the columns we extract from the transaction registry
    extract_col_from_transaction_registry = [
        TransactionRegistryColNameValues.SOURCE_PRICE.value,
        TransactionRegistryColNameValues.SOURCE_VOLUME.value,
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value,
        TransactionRegistryColNameValues.PRICE_PER_UNIT.value,
    ]

    # Fetch all transactions and filter ISIN code
    async with TransactionRegistry() as registry_obj:
        df_transactions = await registry_obj.async_get_registry()

    df_security_holding_history = await SecurityHoldingHistory(
        isin_code=isin_code,
        df_transaction_registry=df_transactions,
    ).async_get_data()

    # Create a date range between start_date and end_date, excluding weekends
    # Set start date to 1980-01-01 to ensure all dates are included
    # Convert the date range to a DataFrame and set index
    df_date_range = await async_get_empty_df_with_datetime_index()

    # Merge the date range DataFrame with df_transactions on the date index
    df_transaction_with_date = df_date_range.join(
        df_security_holding_history[extract_col_from_transaction_registry],
        how="left",
    )

    # Get all market data for the ISIN
    df_market_data = await async_get_market_data(isin_code=isin_code)

    # Merge the resulting DataFrame with df_market_data on the date index
    df_transaction_with_market_data = df_transaction_with_date.join(
        df_market_data[["price"]], how="left"
    )

    # Keep only the date and price columns
    df_result = df_transaction_with_market_data[
        ["price", *extract_col_from_transaction_registry]
    ]

    df_result = await async_filter_df_by_date_range(
        df_to_filter=df_result,
        start_date=start_date,
        end_date=end_date,
    )

    # Fill missing values
    df_result[TransactionRegistryColNameValues.PRICE_PER_UNIT.value] = df_result[
        TransactionRegistryColNameValues.PRICE_PER_UNIT.value
    ].ffill()

    # Fill NaN values with None
    df_result = df_result.replace({np.nan: None})

    for index, row in df_result.iterrows():
        volume_buy = (
            row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
            if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
            == TransactionTypeValues.BUY.value
            else None
        )
        volume_sell = (
            row[TransactionRegistryColNameValues.SOURCE_VOLUME.value]
            if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
            == TransactionTypeValues.SELL.value
            else None
        )
        dividend_per_security = (
            row[TransactionRegistryColNameValues.SOURCE_PRICE.value]
            if row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value]
            == TransactionTypeValues.DIVIDEND.value
            else None
        )

        output_data.append(
            ChartData(
                x_val=pd.to_datetime(index).date(),
                y_val=row["price"],
                volume_buy=volume_buy,
                volume_sell=volume_sell,
                dividend_per_security=dividend_per_security,
                cost_price_average=row[
                    TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ],
            )
        )

    return output_data
