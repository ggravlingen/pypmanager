/**
 * LedgerRow represents a single row in a ledger.
 */
export interface LedgerRow {
  transactionDate?: Date;
  broker?: string;
  source?: string;
  action?: string;
  name?: string;
  noTraded?: number;
  aggBuyVolume?: number;
  averagePrice?: number;
  amount?: number;
  commission?: number;
  cashFlow?: number;
  fx?: number;
  averageFx?: number;
  account?: string;
  credit?: number;
  debit?: number;
}
