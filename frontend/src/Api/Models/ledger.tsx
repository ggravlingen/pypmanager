/**
 * LedgerRow represents a single row in a ledger.
 */
export interface LedgerRow {
  reportDate?: Date;
  broker?: string;
  source?: string;
  action?: string;
  name?: string;
  noTraded?: number;
  aggBuyVolume?: number;
  averagePrice?: number;
  amount?: number;
  commission?: number;
}
