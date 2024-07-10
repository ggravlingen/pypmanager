/**
 * LedgerRow represents a single row in the historical portfolio content.
 */
export interface HistoricalPortfolioRow {
  reportDate?: Date;
  investedAmount?: number;
  marketValue?: number;
  returnPct?: number;
  realizedPnl?: number;
  unrealizedPnl?: number;
}
