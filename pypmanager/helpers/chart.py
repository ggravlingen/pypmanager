"""Chart helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003

import numpy as np
import pandas as pd
import strawberry

from pypmanager.helpers.market_data import get_market_data
from pypmanager.helpers.security_holding_history import SecurityHoldingHistory
from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry
from pypmanager.settings import Settings
from pypmanager.utils.dt import async_get_empty_df_with_datetime_index


@strawberry.type
@dataclass
class ChartData:
    """Define chart data."""

    x_val: date
    y_val: float | None

    volume_buy: float | None
    volume_sell: float | None

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
        TransactionRegistryColNameValues.SOURCE_VOLUME.value,
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value,
    ]

    # Fetch all transactions and filter ISIN code
    df_transactions = await TransactionRegistry().async_get_registry()

    # implement this
    await SecurityHoldingHistory(
        isin_code=isin_code,
        df_transaction_registry=df_transactions,
    ).async_get_data()

    # Create a date range between start_date and end_date, excluding weekends
    # Set start date to 1980-01-01 to ensure all dates are included
    # Convert the date range to a DataFrame and set index
    df_date_range = await async_get_empty_df_with_datetime_index()

    # Merge the date range DataFrame with df_transactions on the date index
    df_transaction_with_date = df_date_range.join(
        df_transactions[extract_col_from_transaction_registry],
        how="left",
    )

    # Get all market data for the ISIN
    df_market_data = get_market_data(isin_code=isin_code)

    # Merge the resulting DataFrame with df_market_data on the date index
    df_transaction_with_market_data = df_transaction_with_date.join(
        df_market_data[["price"]], how="left"
    )

    # Keep only the date and price columns
    df_result = df_transaction_with_market_data[
        ["price", *extract_col_from_transaction_registry]
    ]

    # Filter the relevant start date
    start_date_timestamp = pd.Timestamp(
        start_date
    )  # Convert start_date argument to pandas.Timestamp for comparison
    min_transaction_date = df_result.index.min().tz_localize(None)
    start_date_calc = max(start_date_timestamp, min_transaction_date).tz_localize(
        Settings.system_time_zone
    )

    # Filter the relevant end date
    end_date_timestamp = pd.Timestamp(end_date)
    max_transaction_date = df_result.index.max().tz_localize(None)
    end_date_calc = min(end_date_timestamp, max_transaction_date).tz_localize(
        Settings.system_time_zone
    )

    # Filter the relevant date range
    df_result = df_result[
        (df_result.index >= start_date_calc) & (df_result.index <= end_date_calc)
    ]

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

        output_data.append(
            ChartData(
                x_val=pd.to_datetime(index).date(),
                y_val=row["price"],
                volume_buy=volume_buy,
                volume_sell=volume_sell,
            )
        )

    return output_data
