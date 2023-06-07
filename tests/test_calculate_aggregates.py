"""Test class CalculateAggregates."""

from datetime import datetime

import pandas as pd
from pandas.testing import assert_frame_equal

from pypmanager.loader_transaction.calculate_aggregates_v2 import CalculateAggregates
from pypmanager.loader_transaction.const import ColumnNameValues, TransactionTypeValues


def test_interest_transaction():
    """Test interest transaction."""
    expected_df = pd.DataFrame(
        [
            {
                ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
                ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
                ColumnNameValues.AMOUNT: 100.0,
                ColumnNameValues.REALIZED_PNL_INTEREST: 100.0,
                ColumnNameValues.REALIZED_PNL: 100.0,
            }
        ]
    )
    expected_df = expected_df.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = [
        {
            ColumnNameValues.TRANSACTION_DATE: datetime(2023, 4, 1),
            ColumnNameValues.TRANSACTION_TYPE: TransactionTypeValues.INTEREST,
            ColumnNameValues.AMOUNT: 100.0,
        }
    ]
    df_test = pd.DataFrame(data)
    df_test = df_test.set_index(ColumnNameValues.TRANSACTION_DATE)

    data = CalculateAggregates(security_transactions=df_test)

    assert_frame_equal(data.output_data, expected_df)
