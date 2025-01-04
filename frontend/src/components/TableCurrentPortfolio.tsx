import { QueryLoader, useQueryGetPortfolio } from "@Api";
import { BasicTable, CellAlign, CellDataType } from "@Generic";
import React from "react";

import { ColumnSecurity } from "./common";

const columnSettings = [
  {
    headerName: "Security",
    fieldPath: "",
    align: CellAlign.LEFT,
    dataType: CellDataType.CUSTOM,
    description: "The name of the security",
    customComponent: ColumnSecurity,
  },
  {
    fieldPath: "marketValueDate",
    headerName: "Date of market value",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
  },
  {
    fieldPath: "currentMarketValueAmount",
    headerName: "Market value",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    showSubtotal: true,
  },
  {
    fieldPath: "investedAmount",
    headerName: "Invested amount",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    showSubtotal: true,
  },
  {
    fieldPath: "quantityHeld",
    headerName: "Number of units",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
  },
  {
    fieldPath: "costBaseAverage",
    headerName: "Average cost",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
  },
  {
    fieldPath: "marketValuePrice",
    headerName: "Price",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    fieldPath: "pnlTotal",
    headerName: "Total P&L",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    showSubtotal: true,
    description: "Total profit and loss.",
  },
  {
    fieldPath: "pnlTrade",
    headerName: "P&L - trade",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    showSubtotal: true,
    description: "Profit and loss from buying and selling securities.",
  },
  {
    fieldPath: "pnlDividend",
    headerName: "P&L - dividend",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    showSubtotal: true,
    description: "Profit and loss from dividends.",
  },
  {
    fieldPath: "pnlUnrealized",
    headerName: "P&L - unrealized",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    showSubtotal: true,
    description: "Profit and loss from unrealized results.",
  },
];

/**
 * Renders a table displaying the current portfolio.
 *
 * This component fetches portfolio data using a custom hook `useQueryGetPortfolio` and displays it
 * in a `BasicTable` component. It handles loading and error states with a `QueryLoader` component,
 * which displays appropriate feedback to the user based on the query's state. The `BasicTable` component
 * is configured with predefined `columnSettings` to format and display the portfolio data.
 * @returns A component that displays the current portfolio in a table format.
 */
export default function TableCurrentPortfolio(): React.JSX.Element {
  const { data, loading, error } = useQueryGetPortfolio();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable
        data={data?.currentPortfolio}
        columnSettings={columnSettings}
      />
    </QueryLoader>
  );
}
