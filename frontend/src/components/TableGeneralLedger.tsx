import { QueryLoader, useQueryGetLedger } from "@Api";
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
    fieldPath: "broker",
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
    headerName: "Name",
    fieldPath: "name",
    align: CellAlign.LEFT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Volume",
    fieldPath: "noTraded",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Held post trade",
    fieldPath: "aggBuyVolume",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Average price",
    fieldPath: "averagePrice",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Amount",
    fieldPath: "amount",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Commission",
    fieldPath: "commission",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Cash flow",
    fieldPath: "cashFlow",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "FX",
    fieldPath: "fx",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Average FX rate",
    fieldPath: "averageFx",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Account",
    fieldPath: "account",
    align: CellAlign.RIGHT,
    dataType: CellDataType.STRING,
  },
  {
    headerName: "Credit",
    fieldPath: "credit",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
  {
    headerName: "Debit",
    fieldPath: "debit",
    align: CellAlign.RIGHT,
    dataType: CellDataType.NUMBER,
  },
];

/**
 * TableGeneralLedger component that renders a table displaying general ledger data.
 * It utilizes the `useQueryGetLedger` hook to fetch ledger data and handles loading,
 * error states, and data rendering through the `QueryLoader` component.
 *
 * The table is designed to display various details about transactions including
 * transaction date, broker, source, action, name, volume, held post trade,
 * average price, amount, and commission. Data formatting is applied to numerical
 * values for better readability.
 * @returns A component that renders a table filled with general ledger data.
 */
export default function TableGeneralLedger(): JSX.Element {
  const { data, loading, error } = useQueryGetLedger();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable
        data={data?.allGeneralLedger}
        columnSettings={columnSettings}
      />
    </QueryLoader>
  );
}
