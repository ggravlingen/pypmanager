import { QueryLoader, useQueryGetLedger } from "@Api";
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { formatDate, formatNumber } from "@Utils";
import React from "react";

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
      <TableContainer component={Paper} style={{ maxHeight: "100vh" }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell align="right">Transaction date</TableCell>
              <TableCell>Broker</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Name</TableCell>
              <TableCell align="right">Volume</TableCell>
              <TableCell align="right">Held post trade</TableCell>
              <TableCell align="right">Average price</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell align="right">Commission</TableCell>
              <TableCell align="right">Cash flow</TableCell>
              <TableCell align="right">FX</TableCell>
              <TableCell align="right">Average FX rate</TableCell>
              <TableCell align="right">Account</TableCell>
              <TableCell align="right">Credit</TableCell>
              <TableCell>Debit</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.allGeneralLedger.map((row, index) => (
              <TableRow key={index}>
                <TableCell align="right">
                  {formatDate(row.transactionDate)}
                </TableCell>
                <TableCell>{row.broker}</TableCell>
                <TableCell>{row.source}</TableCell>
                <TableCell>{row.action}</TableCell>
                <TableCell>{row.name}</TableCell>
                <TableCell align="right">
                  {formatNumber(row.noTraded)}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(row.aggBuyVolume, 0)}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(row.averagePrice, 1)}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(row.amount, 0)}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(row.commission, 0)}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(row.cashFlow, 0)}
                </TableCell>
                <TableCell align="right">{formatNumber(row.fx, 4)}</TableCell>
                <TableCell align="right">
                  {formatNumber(row.averageFx, 4)}
                </TableCell>
                <TableCell>{row.account}</TableCell>
                <TableCell align="right">
                  {formatNumber(row.credit, 0)}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(row.debit, 0)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </QueryLoader>
  );
}
