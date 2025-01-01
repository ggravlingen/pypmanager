export interface BaseTransactionRow {
    transactionDate?: Date;
    isinCode?: string;
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
    quantityHeld?: number;
    pnlTotal?: number;
    pnlTrade?: number;
    pnlDividend?: number;
  }