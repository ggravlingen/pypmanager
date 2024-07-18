import { QueryLoader, useQueryGetAllTransaction } from "@Api";
import { BasicTable, CellAlign, CellDataType } from "@Generic";
import React from "react";

const columnSettings = [
  {
    headerName: "Transaction date",
    fieldPath: "transactionDate",
    align: CellAlign.RIGHT,
    dataType: CellDataType.DATE,
  },
  {
    headerName: "Broker",
    fieldPath: "Broker",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Source",
    fieldPath: "source",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Action",
    fieldPath: "action",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Security",
    fieldPath: "name",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Volume",
    fieldPath: "noTraded",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
  },
  {
    headerName: "Price",
    fieldPath: "price",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 2,
  },
  {
    headerName: "Commission",
    fieldPath: "commission",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
  },
  {
    headerName: "Currency",
    fieldPath: "currency",
    align: CellAlign.RIGHT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Nominal cash flow",
    fieldPath: "cashFlow",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 0,
  },
  {
    headerName: "FX rate",
    fieldPath: "fx",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
    noDecimal: 4,
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
