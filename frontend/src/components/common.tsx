import type { TransactionRow } from "@Api";
import { Box } from "@mui/material";
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
export function ColumnSecurity({
  rowData,
}: {
  rowData: TransactionRow;
}): React.JSX.Element {
  const securityName = rowData.name ? rowData.name : "No name";

  return (
    <Box>
      {rowData.isinCode ? (
        <Link to={`/chart/${rowData.isinCode}`}>{securityName}</Link>
      ) : (
        securityName
      )}
    </Box>
  );
}
