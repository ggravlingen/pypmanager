export interface PortfolioContentRow {
  name?: string;
  isinCode?: string | null;
  quantityHeld?: number | null;
  costBaseAverage?: number | null;
  currentMarketValueAmount?: number;
  investedAmount?: number | null;
  pnlTotal?: number | null;
  pnlTrade?: number | null;
  pnlDividend?: number | null;
  pnlUnrealized?: number | null;
  marketValueDate?: Date | null;
  marketValuePrice?: number | null;
}
