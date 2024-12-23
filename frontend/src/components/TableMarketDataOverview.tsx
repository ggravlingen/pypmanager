import { QueryLoader, useQueryMarketDataOverview } from "@Api";
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
    headerName: "Start",
    fieldPath: "firstDate",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
    description: "The first date of the market data",
  },
  {
    headerName: "End",
    fieldPath: "lastDate",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
    description: "The last date of the market data",
  },
];

/**
 * Renders a table component displaying market data overview.
 * @returns The JSX element representing the table component.
 */
export default function TableMarketDataOverview(): JSX.Element {
  const { data, loading, error } = useQueryMarketDataOverview();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable
        data={data?.marketDataOverview}
        columnSettings={columnSettings}
      />
    </QueryLoader>
  );
}
