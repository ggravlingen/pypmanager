import { QueryLoader, useQueryGetHistoricalPortfolio } from "@Api";
import { BasicTable, CellAlign, CellDataType } from "@Generic";
import React from "react";

const columnSettings = [
  {
    headerName: "Report date",
    fieldPath: "reportDate",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
  },
  {
    headerName: "Invested amount",
    fieldPath: "investedAmount",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
  },
  {
    headerName: "Market value",
    fieldPath: "marketValue",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
  },
  {
    headerName: "Return %",
    fieldPath: "returnPct",
    align: CellAlign.RIGHT,
    dataType: CellDataType.PER_CENT,
  },
  {
    headerName: "Realized PnL",
    fieldPath: "realizedPnl",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
  },
  {
    headerName: "Unrealized PnL",
    fieldPath: "unrealizedPnl",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
  },
];

/**
 * Renders a table displaying historical portfolio data.
 *
 * This component fetches historical portfolio data using the `useQueryGetHistoricalPortfolio` hook,
 * then displays the data in a `BasicTable` component. It also handles loading and error states
 * with the `QueryLoader` component.
 * @returns A component that renders a table with historical portfolio data.
 */
export default function TableHistoricalPortfolio(): JSX.Element {
  const { data, loading, error } = useQueryGetHistoricalPortfolio();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable
        data={data?.historicalPortfolio}
        columnSettings={columnSettings}
      />
    </QueryLoader>
  );
}
