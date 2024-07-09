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

import { formatDate } from "@Utils";

export default function TableGeneralLedger(): JSX.Element {
  const { data } = useQueryGetLedger();

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Broker</TableCell>
            <TableCell>Source</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.allGeneralLedger.map((row, index) => (
            <TableRow key={index}>
              <TableCell>{formatDate(row.reportDate)}</TableCell>
              <TableCell>{row.broker}</TableCell>
              <TableCell>{row.source}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
