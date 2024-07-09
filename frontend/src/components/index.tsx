import React from "react";
import { useQueryGetLedger } from "@Api";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

import { formatDate, formatNumber } from "@Utils";

export default function TableGeneralLedger(): JSX.Element {
  const { data } = useQueryGetLedger();

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <TableContainer component={Paper} style={{ maxHeight: "80vh" }}>
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
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.allGeneralLedger.map((row, index) => (
            <TableRow key={index}>
              <TableCell align="right">{formatDate(row.reportDate)}</TableCell>
              <TableCell>{row.broker}</TableCell>
              <TableCell>{row.source}</TableCell>
              <TableCell>{row.action}</TableCell>
              <TableCell>{row.name}</TableCell>
              <TableCell align="right">{formatNumber(row.noTraded)}</TableCell>
              <TableCell align="right">
                {formatNumber(row.aggBuyVolume, 0)}
              </TableCell>
              <TableCell align="right">
                {formatNumber(row.averagePrice, 1)}
              </TableCell>
              <TableCell align="right">{formatNumber(row.amount, 0)}</TableCell>
              <TableCell align="right">
                {formatNumber(row.commission, 0)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
