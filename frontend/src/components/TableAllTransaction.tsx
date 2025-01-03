import type { TransactionRow } from "@Api";
import {
  QueryLoader,
  TransactionTypeValues,
  useQueryGetAllTransaction,
} from "@Api";
import { BasicTable, CellAlign, CellDataType } from "@Generic";
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Tooltip,
} from "@mui/material";
import { formatNumber } from "@Utils";
import React from "react";

import { ColumnSecurity } from "./common";

/**
 * Renders the PnL column for a transaction row.
 * @param rowData - The data for the transaction row.
 * @param rowData.rowData - The data for the transaction row.
 * @returns The JSX element representing the PnL column.
 */
function ColumnPnL({
  rowData,
}: {
  rowData: TransactionRow;
}): React.JSX.Element {
  return (
    <Tooltip
      title={
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>Total PnL</TableCell>
              <TableCell>{formatNumber(rowData.pnlTotal, 0, false)}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>... of which from trading</TableCell>
              <TableCell>{formatNumber(rowData.pnlTrade, 0, false)}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>... of which from dividends</TableCell>
              <TableCell>
                {formatNumber(rowData.pnlDividend, 0, false)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      }
      arrow
    >
      <Box>{formatNumber(rowData.pnlTotal, 0, false)}</Box>
    </Tooltip>
  );
}

/**
 * Renders the price column for a transaction row.
 * @param props - The component props.
 * @param props.rowData - The data for the transaction row.
 * @returns The rendered price column.
 */
function ColumnPrice({
  rowData,
}: {
  rowData: TransactionRow;
}): React.JSX.Element {
  return (
    <Tooltip
      title={
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>Currency</TableCell>
              <TableCell align="right">{rowData.currency}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>FX rate</TableCell>
              <TableCell align="right">
                {formatNumber(rowData.fx, 4, false)}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      }
      arrow
    >
      <Box>{formatNumber(rowData.price, 2, false)}</Box>
    </Tooltip>
  );
}

/**
 * Component to display the quantity held in a table row.
 * @param props - The component props.
 * @param props.rowData - The data for the table row.
 * @returns The JSX element representing the quantity held.
 * This component checks if the transaction is a "Sell" action and if the quantity held is zero or not defined.
 * If both conditions are met, it displays a dash ("-"). Otherwise, it formats and displays the quantity held.
 */
function ColumnNoHeld({
  rowData,
}: {
  rowData: TransactionRow;
}): React.JSX.Element {
  if (
    rowData.noTraded &&
    rowData.action &&
    rowData.action.toLowerCase() === TransactionTypeValues.SELL &&
    (rowData.quantityHeld === 0 || !rowData.quantityHeld)
  ) {
    return <Box>-</Box>;
  }
  return <Box>{formatNumber(rowData.quantityHeld, 0, false)}</Box>;
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
    fieldPath: "",
    align: CellAlign.LEFT,
    dataType: CellDataType.CUSTOM,
    description: "The name of the security",
    customComponent: ColumnSecurity,
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
    fieldPath: "",
    align: CellAlign.RIGHT,
    dataType: CellDataType.CUSTOM,
    customComponent: ColumnNoHeld,
    description: "The number of units held efter the transaction",
  },
  {
    headerName: "Price",
    fieldPath: "price",
    align: CellAlign.RIGHT,
    dataType: CellDataType.CUSTOM,
    customComponent: ColumnPrice,
    description:
      "The price paid or received for the security. Hover cell for details.",
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
      "The total profit or loss for the transaction. Hover cell for details.",
  },
];

/**
 * Renders a table component displaying all historical transactions.
 * @returns The JSX element representing the table component.
 */
export default function TableAllTransaction(): React.JSX.Element {
  const { data, loading, error } = useQueryGetAllTransaction();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable data={data?.allTransaction} columnSettings={columnSettings} />
    </QueryLoader>
  );
}
