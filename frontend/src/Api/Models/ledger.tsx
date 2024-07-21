/**
 * LedgerRow represents a single row in a ledger.
 */

export interface BaseTransactionRow {
  transactionDate?: Date;
  broker?: string;
  source?: string;
  action?: string;
  name?: string;
  noTraded?: number;
  commission?: number;
  fx?: number;
}

export interface TransactionRow extends BaseTransactionRow {
  price?: number;
  currency?: string;
  cashFlow?: number;
  costBaseAverage?: number;
}

export interface LedgerRow extends BaseTransactionRow {
  aggBuyVolume?: number;
  averagePrice?: number;
  amount?: number;
  cashFlow?: number;
  averageFx?: number;
  account?: string;
  credit?: number;
  debit?: number;
}
