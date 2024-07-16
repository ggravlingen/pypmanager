import { QueryLoader, useQueryGetIncomeStatement } from "@Api";
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { formatNumber } from "@Utils";
import React from "react";

type MapStatementType = {
  [key: string]: string;
};

const MAP_STATEMENT: MapStatementType = {
  is_interest: "Interest income",
  is_dividends: "Dividend income",
  is_trading: "Trading income",
};

/**
 * Renders a table component for displaying the income statement.
 * @returns JSX.Element representing the table component.
 */
export default function TableIncomeStatement(): JSX.Element {
  const { data, loading, error } = useQueryGetIncomeStatement();

  return (
    <QueryLoader loading={loading} data={data} error={error}>
      <TableContainer component={Paper} style={{ maxHeight: "100vh" }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell />
              {data?.resultStatement[0].yearList
                .slice()
                .reverse()
                .map((year) => (
                  <TableCell key={year} align="right">
                    {year}
                  </TableCell>
                ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.resultStatement.map(({ itemName, yearList, amountList }) => (
              <TableRow key={itemName}>
                <TableCell>{MAP_STATEMENT[itemName]}</TableCell>
                {yearList
                  .slice()
                  .reverse()
                  .map((year, index) => (
                    <TableCell key={year} align="right">
                      {formatNumber(
                        amountList[yearList.length - 1 - index],
                        0,
                        false,
                      )}
                    </TableCell>
                  ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </QueryLoader>
  );
}
