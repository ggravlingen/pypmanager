"""Chart helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003

import numpy as np
import pandas as pd
import strawberry

from pypmanager.analytics.holding import get_market_data
from pypmanager.ingest.transaction.const import (
    TransactionRegistryColNameValues,
    TransactionTypeValues,
)
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry


@strawberry.type
@dataclass
class ChartData:
    """Define chart data."""

    x_val: date
    y_val: float | None

    volume_buy: float | None
    volume_sell: float | None

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

    # Fetch all transactions
    df_transactions = await TransactionRegistry().async_get_registry()

    # Filter transactions by ISIN code
    df_transactions = df_transactions.query("source_isin_code == @isin_code")

    # Append the source transaction date as a column if it does not exist
    if (
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value
        not in df_transactions.columns
    ):
        df_transactions[
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value
        ] = df_transactions.index

    # Filter the relevant start date
    start_date_calc = max(
        # Convert start_date to pandas.Timestamp for comparison
        pd.Timestamp(start_date),
        df_transactions[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value]
        .min()
        .tz_localize(None),
    )

    # Filter the relevant end date
    end_date_calc = max(
        # Convert start_date to pandas.Timestamp for comparison
        pd.Timestamp(end_date),
        df_transactions[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value]
        .max()
        .tz_localize(None),
    )

    # Create a date range between start_date and end_date, excluding weekends
    date_range = pd.date_range(start=start_date_calc, end=end_date_calc, freq="B")

    # Convert the date range to a DataFrame
    df_date_range = pd.DataFrame(date_range, columns=["date"])

    # Ensure the date column is the index and formatted as yyyy-mm-dd
    df_date_range["date"] = df_date_range["date"].dt.strftime("%Y-%m-%d")
    df_date_range = df_date_range.set_index("date")

    df_transactions[TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value] = (
        df_transactions[
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value
        ].dt.strftime("%Y-%m-%d")
    )
    df_transactions = df_transactions.set_index(
        TransactionRegistryColNameValues.SOURCE_TRANSACTION_DATE.value
    )

    # Merge the date range DataFrame with df_transactions on the date index
    df_transaction_with_date = df_date_range.join(
        df_transactions[
            [
                TransactionRegistryColNameValues.SOURCE_VOLUME.value,
                TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value,
            ]
        ],
        how="left",
    )

    # Get all market data for the ISIN
    df_market_data = get_market_data(isin_code=isin_code)

    # Merge the date range DataFrame with df_market_data on the date index
    df_market_data.index = pd.to_datetime(df_market_data.index).strftime("%Y-%m-%d")

    # Merge the resulting DataFrame with df_market_data on the date index
    df_transaction_with_market_data = df_transaction_with_date.join(
        df_market_data[["price"]], how="left"
    )

    # Keep only the date and price columns
    df_result = df_transaction_with_market_data[
        [
            "price",
            TransactionRegistryColNameValues.SOURCE_VOLUME.value,
            TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value,
        ]
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
