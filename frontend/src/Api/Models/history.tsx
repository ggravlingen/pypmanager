/**
 * LedgerRow represents a single row in the historical portfolio content.
 */
export interface HistoricalPortfolioRow {
  reportDate?: Date;
  invested_amount?: number;
  marketValue?: number;
  returnPct?: number;
  totalPnl?: number;
  realizedPnl?: number;
  unrealizedPnl?: number;
}
