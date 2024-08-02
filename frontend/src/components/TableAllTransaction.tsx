import { QueryLoader, TransactionRow, useQueryGetAllTransaction } from "@Api";
import { BasicTable, CellAlign, CellDataType } from "@Generic";
import { formatNumber } from "@Utils";
import React from "react";

/**
 * Renders the PnL column for a transaction row.
 * @param rowData - The data for the transaction row.
 * @param rowData.rowData - The data for the transaction row.
 * @returns The JSX element representing the PnL column.
 */
function ColumnPnL({ rowData }: { rowData: TransactionRow }): JSX.Element {
  return <>{formatNumber(rowData.pnlTotal, 0, false)}</>;
}

const columnSettings = [
  {
    headerName: "Transaction date",
    fieldPath: "transactionDate",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
    description: "The date of the transaction",
  },
  {
    headerName: "Broker",
    fieldPath: "broker",
    align: CellAlign.CENTER,
    dataType: CellDataType.STRING,
    description: "The broker used for the transaction",
  },
  {
    headerName: "Source",
    fieldPath: "source",
    align: CellAlign.CENTER,
    dataType: CellDataType.STRING,
    description: "The data source file of the transaction",
  },
  {
    headerName: "Security",
    fieldPath: "name",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
    description: "The name of the security",
  },
  {
    headerName: "Action",
    fieldPath: "action",
    align: CellAlign.CENTER,
    dataType: CellDataType.STRING,
    description: "The type of transaction",
  },
  {
    headerName: "Volume",
    fieldPath: "noTraded",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
    description: "The number of securities traded",
  },
  {
    headerName: "Held",
    fieldPath: "quantityHeld",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    description: "The number of units held efter the transaction",
  },
  {
    headerName: "Price",
    fieldPath: "price",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
    description: "The price paid or received for the security",
  },
  {
    headerName: "Cost base average",
    fieldPath: "costBaseAverage",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
    description: "The volume weighted average price paid for the security",
  },
  {
    headerName: "Commission",
    fieldPath: "commission",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    description: "The commission paid, if any",
  },
  {
    headerName: "Currency",
    fieldPath: "currency",
    align: CellAlign.RIGHT,
    dataType: CellDataType.STRING,
    description: "The nominal currency of the transaction",
  },
  {
    headerName: "Nominal cash flow",
    fieldPath: "cashFlow",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
    description: "The nominal cash flow, net of any fees, for the transaction",
  },
  {
    headerName: "PnL",
    fieldPath: "",
    align: CellAlign.RIGHT,
    dataType: CellDataType.CUSTOM,
    customComponent: ColumnPnL,
    description:
      "The total profit or loss for the transaction, including any commission.",
  },
];

/**
 * Renders a table component displaying all historical transactions.
 * @returns The JSX element representing the table component.
 */
export default function TableAllTransaction(): JSX.Element {
  const { data, loading, error } = useQueryGetAllTransaction();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable data={data?.allTransaction} columnSettings={columnSettings} />
    </QueryLoader>
  );
}
