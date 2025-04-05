"""Helpers for transactions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
from typing import cast

import numpy as np
import strawberry

from pypmanager.ingest.transaction.const import TransactionRegistryColNameValues
from pypmanager.ingest.transaction.transaction_registry import TransactionRegistry


@strawberry.type
@dataclass
class TransactionRow:
    """Represent a transaction row."""

    transaction_date: date
    broker: str
    source: str
    action: str
    name: str | None
    no_traded: float | None
    commission: float | None
    fx: float | None
    isin_code: str | None
    price: float | None
    currency: str | None
    cash_flow: float | None
    cost_base_average: float | None
    pnl_total: float | None
    pnl_trade: float | None
    pnl_dividend: float | None
    quantity_held: float | None


async def async_get_all_transactions() -> list[TransactionRow]:
    """Get all transactions."""
    async with TransactionRegistry(sort_by_date_descending=True) as registry_obj:
        transaction_list = await registry_obj.async_get_registry()

    transaction_list = transaction_list.replace({np.nan: None})

    output_list: list[TransactionRow] = []
    for index, row in transaction_list.iterrows():
        if row[TransactionRegistryColNameValues.SOURCE_FEE.value] is not None:
            commission = row[TransactionRegistryColNameValues.SOURCE_FEE.value]
        else:
            commission = None

        if (
            row[TransactionRegistryColNameValues.SOURCE_ISIN.value] is not None
            and row[TransactionRegistryColNameValues.SOURCE_ISIN.value] != 0
            and row[TransactionRegistryColNameValues.SOURCE_ISIN.value] != "None"
        ):
            isin_code = row[TransactionRegistryColNameValues.SOURCE_ISIN.value]
        else:
            isin_code = None

        output_list.append(
            TransactionRow(
                transaction_date=index,
                isin_code=isin_code,
                broker=row[TransactionRegistryColNameValues.SOURCE_BROKER.value],
                source=row[TransactionRegistryColNameValues.SOURCE_FILE.value],
                action=cast(
                    "str",
                    row[TransactionRegistryColNameValues.SOURCE_TRANSACTION_TYPE.value],
                ).capitalize(),
                name=row[TransactionRegistryColNameValues.SOURCE_NAME_SECURITY.value],
                no_traded=row[TransactionRegistryColNameValues.SOURCE_VOLUME.value],
                currency=row[TransactionRegistryColNameValues.SOURCE_CURRENCY.value],
                price=row[TransactionRegistryColNameValues.SOURCE_PRICE.value],
                # It makes more sense to use the absolute value of the commission in
                # this context
                commission=commission,
                cash_flow=row[
                    TransactionRegistryColNameValues.CASH_FLOW_NET_FEE_NOMINAL.value
                ],
                fx=row[TransactionRegistryColNameValues.SOURCE_FX.value],
                cost_base_average=row[
                    TransactionRegistryColNameValues.PRICE_PER_UNIT.value
                ],
                pnl_total=row[TransactionRegistryColNameValues.CALC_PNL_TOTAL.value],
                pnl_trade=row[TransactionRegistryColNameValues.CALC_PNL_TRADE.value],
                pnl_dividend=row[
                    TransactionRegistryColNameValues.CALC_PNL_DIVIDEND.value
                ],
                quantity_held=row[
                    TransactionRegistryColNameValues.ADJUSTED_QUANTITY_HELD.value
                ],
            )
        )

    return output_list
