export interface PortfolioContentRow {
  name?: string;
  dateMarketValue?: Date | null;
  investedAmount?: number | null;
  marketValue?: number | null;
  currentHoldings?: number | null;
  currentPrice?: number | null;
  averagePrice?: number | null;
  returnPct?: number | null;
  totalPnl?: number;
  realizedPnl?: number;
  unrealizedPnl?: number;
}
