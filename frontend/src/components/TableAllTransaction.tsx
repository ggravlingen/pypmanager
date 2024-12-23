import { QueryLoader, TransactionRow, useQueryGetAllTransaction } from "@Api";
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
import { Link } from "react-router-dom";

/**
 * Component to render a column displaying security information.
 * If the `isinCode` is present in the `rowData`, it renders a link to the chart page for that security.
 * Otherwise, it simply displays the name of the security.
 * @param props - The component props.
 * @param props.rowData - The data for the row, containing security information.
 * @returns The rendered column with security information.
 */
function ColumnSecurity({ rowData }: { rowData: TransactionRow }): JSX.Element {
  return (
    <Box>
      {rowData.isinCode ? (
        <Link to={`/chart/${rowData.isinCode}`}>{rowData.name}</Link>
      ) : (
        rowData.name
      )}
    </Box>
  );
}

/**
 * Renders the PnL column for a transaction row.
 * @param rowData - The data for the transaction row.
 * @param rowData.rowData - The data for the transaction row.
 * @returns The JSX element representing the PnL column.
 */
function ColumnPnL({ rowData }: { rowData: TransactionRow }): JSX.Element {
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
function ColumnPrice({ rowData }: { rowData: TransactionRow }): JSX.Element {
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
export default function TableAllTransaction(): JSX.Element {
  const { data, loading, error } = useQueryGetAllTransaction();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <BasicTable data={data?.allTransaction} columnSettings={columnSettings} />
    </QueryLoader>
  );
}
