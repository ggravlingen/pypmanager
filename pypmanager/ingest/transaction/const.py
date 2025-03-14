"""Constants."""

from __future__ import annotations

from enum import StrEnum
import logging


class TransactionTypeValues(StrEnum):
    """Represent transaction types."""

    BUY = "buy"
    CASHBACK = "cashback"
    DEPOSIT = "deposit"
    DIVIDEND = "dividend"
    FEE = "fee"
    FEE_CREDIT = "fee_credit"
    INTEREST = "interest"
    SELL = "sell"
    TAX = "tax"
    WITHDRAW = "withdraw"


class AccountNameValues(StrEnum):
    """Represent names of accounts."""

    CASH = "cash"
    EQUITY = "equity"
    SECURITIES = "securities"
    IS_PNL = "is_trading"
    IS_CASHBACK = "is_cashback"
    IS_DIVIDEND = "is_dividends"
    IS_INTEREST = "is_interest"
    IS_FEE = "is_costs_fee"
    IS_TAX = "is_costs_tax"


class CurrencyValues(StrEnum):
    """Represent names of currencies."""

    SEK = "SEK"


class ColumnNameValues(StrEnum):
    """Represent names of columns in the ledger."""

    ACCOUNT = "ledger_account"
    AVG_PRICE = "average_price"
    AVG_FX = "average_fx_rate"
    AMOUNT = "amount"
    """
    The cash flow amount of the transaction.

    Use turnover if the value represend a buy or a sell.
    """
    CASH_FLOW_LOCAL = "cash_flow_base_ccy"
    CREDIT = "credit"
    DEBIT = "debit"
    NO_HELD = "cumulative_buy_volume"
    REALIZED_PNL = "realized_pnl"
    REALIZED_PNL_EQ = "realized_pnl_equity"
    REALIZED_PNL_COMMISSION = "realized_pnl_commission"
    REALIZED_PNL_FX = "realized_pnl_fx"
    REALIZED_PNL_INTEREST = "realized_pnl_interest"
    REALIZED_PNL_DIVIDEND = "realized_pnl_dividend"
    TRANSACTION_TYPE_INTERNAL = "transaction_type_internal"
    CF_EX_COMMISSION = "cf_ex_commission"
    COST_BASIS_DELTA = "cost_basis_delta"
    SUM_COST_BASIS_DELTA = "sum_cost_basis_delta"
    TRANSACTION_CASH_FLOW = "transaction_cash_flow"


class TransactionRegistryColNameValues(StrEnum):
    """Represent names of columns in the ledger."""

    ADJUSTED_QUANTITY_HELD = "calc_agg_sum_quantity_held"
    """The aggregate number of units held at the end of the transaction."""
    CASH_FLOW_NET_FEE_NOMINAL = "calc_cf_net_fee_nominal_ccy"
    """The nominal cash flow, net of any fees (eg commissions) in the base currency."""
    CASH_FLOW_GROSS_FEE_NOMINAL = "calc_cf_gross_fee_nominal_ccy"
    """The nominal cash flow, less any fees (eg commissions) in the base currency."""
    INTERNAL_TURNOVER = "internal_turnover"
    """
    An internal turnover column for the ledger.

    Do not expose this to the user.

    This is the absolute value of a transaction's cash flow.
    """
    META_TRANSACTION_YEAR = "meta_transaction_year"
    """The year of the transaction (based on transaction date)."""
    CALC_ADJUSTED_QUANTITY_HELD_IS_RESET = "calc_agg_sum_quantity_held_is_reset"
    """True if all securities have been sold and the adjusted average cost is reset."""
    CALC_TURNOVER_OR_OTHER_CF = "calc_turnover_or_cash_flow"
    """
    Either return turnover or other cash flow.

    Turnover = quantity * price
    Other cash flow = any other flow, eg dividends, fees, etc.
    """
    CALC_PNL_DIVIDEND = "calc_pnl_transaction_dividend"
    """Profit from dividends."""
    CALC_PNL_INTEREST = "calc_pnl_transaction_interest"
    """Profit or loss from interest."""
    CALC_PNL_TOTAL = "calc_pnl_transaction_total"
    """Profit or loss of the transaction."""
    CALC_PNL_TRADE = "calc_pnl_transaction_trade"
    """Total profit or loss for a sell transaction."""
    PRICE_PER_UNIT = "calc_avg_price_per_unit"
    """
    Average purchase price per unit.

    Resets when the cumulative volume held is zero.
    """
    SOURCE_ACCOUNT_NAME = "source_account_name"
    """
    The name of the account the transaction is associated with.

    This value, if present, is ingested from the transaction source files.
    """
    SOURCE_BROKER = "source_broker"
    """
    The name of the broker transactions are ingested from.

    Ingested from the transaction source files.
    """
    SOURCE_CURRENCY = "source_currency"
    """
    The currency of the transaction.

    Ingested from the transaction source files.
    """
    SOURCE_CURRENCY_NOMINAL = "source_currency_nominal"
    """
    The nominal of the transaction.

    Ingested from the transaction source files.
    """
    SOURCE_FILE = "source_file_name"
    """
    The name of the file the transaction was ingested from.

    Ingested from the transaction source files.
    """
    SOURCE_ISIN = "source_isin_code"
    """
    The ISIN code of the security.

    Ingested from the transaction source files
    """
    SOURCE_FEE = "source_fee"
    """
    Any fees associated with the transaction.

    Ingested from the transaction source files.
    """
    SOURCE_FX = "source_fx_rate"
    """
    The FX rate between the nominal currency and your base currency.

    Ingested from the transaction source files.
    """
    SOURCE_NAME_SECURITY = "source_name"
    """
    The full name of the security.

    Ingested from the transaction source files
    """
    SOURCE_OTHER_CASH_FLOW = "source_other_cash_flow"
    """
    Other cash flows associated with a transaction.

    Example of this are dividends, deposits or withdrawals that are not calculated on
    a per unit basis.

    Ingested from the transaction source files.
    """
    SOURCE_PRICE = "source_price"
    """
    Price paid per unit.

    Ingested from the transaction source files.
    """
    SOURCE_TRANSACTION_DATE = "source_transaction_date"
    """
    The date of the transaction (time zone aware).

    Ingested from the transaction source files.
    """
    SOURCE_TRANSACTION_TYPE = "source_transaction_type"
    """
    The type of transaction, eg buy, sell, dividend, etc.

    Ingested from the transaction source files.
    """
    SOURCE_VOLUME = "source_volume"
    """
    The number of units traded.

    Ingested from the transaction source files.
    """


class CSVSeparator(StrEnum):
    """Represent CSV-file separators."""

    COMMA = ","
    SEMI_COLON = ";"


NUMBER_COLS = [
    ColumnNameValues.AMOUNT,
    TransactionRegistryColNameValues.SOURCE_FEE,
    TransactionRegistryColNameValues.SOURCE_FX,
    TransactionRegistryColNameValues.SOURCE_VOLUME,
    TransactionRegistryColNameValues.SOURCE_PRICE,
    ColumnNameValues.REALIZED_PNL,
]


LOGGER = logging.getLogger(__package__)
