import { QueryLoader, useQueryGetPortfolio } from "@Api";
import { BasicTable, CellAlign, CellDataType } from "@Generic";
import React from "react";

const columnSettings = [
  {
    headerName: "Name",
    fieldPath: "name",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
  },
  {
    fieldPath: "dateMarketValue",
    headerName: "Date of market value",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
  },
  {
    fieldPath: "investedAmount",
    headerName: "Invested amount",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 0,
  },
  {
    fieldPath: "marketValue",
    headerName: "Market value",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 0,
  },
  {
    fieldPath: "currentHoldings",
    headerName: "Current holdings",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 0,
  },
  {
    fieldPath: "currentPrice",
    headerName: "Current price",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 2,
  },
  {
    fieldPath: "averagePrice",
    headerName: "Average price",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    fieldPath: "returnPct",
    headerName: "Return %",
    align: CellAlign.RIGHT,
    dataType: CellDataType.PER_CENT,
    noDecimals: 0,
  },
  {
    fieldPath: "totalPnl",
    headerName: "Total P&L",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 0,
  },
  {
    fieldPath: "realizedPnl",
    headerName: "Realized P&L",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 0,
  },
  {
    fieldPath: "unrealizedPnl",
    headerName: "Unrealized P&L",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimals: 0,
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
export default function TableCurrentPortfolio(): JSX.Element {
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
