import { HelpOutline } from "@mui/icons-material";
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TableRow,
  Tooltip,
} from "@mui/material";
import { extractDataFromRecord, formatDate, formatNumber } from "@Utils";
import React from "react";

export enum CellAlign {
  RIGHT = "right",
  CENTER = "center",
  INHERIT = "inherit",
  LEFT = "left",
  JUSTIFY = "justify",
}

export enum CellDataType {
  DATE = "date",
  DATE_RELATIVE = "date_relative",
  NUMBER = "number",
  PER_CENT = "per_cent",
  STRING = "string",
  CUSTOM = "custom",
}

interface ColumnSetting {
  headerName: string;
  fieldPath: string;
  align: CellAlign;
  dataType: CellDataType;
  noDecimal?: number;
  showSubtotal?: boolean;
  description?: string;
  // We must allow any here as row data can by be anything
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  customComponent?: (rowData: any) => React.JSX.Element;
}

interface BasicTableProps {
  // We must use any[] here because the data can be of any type
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[] | undefined;
  columnSettings: ColumnSetting[];
}

/**
 * Extracts and formats a cell value from a row data object based on the column setting.
 *
 * This function takes a column setting, which includes the field path and data type, and
 * a row data object. It first extracts the value from the row data based on the field path.
 * If the value is undefined, it returns null. Otherwise, it formats the value based on the
 * specified data type in the column setting (e.g., date, number) and returns the formatted value.
 * @param columnSetting - The settings for the column, including field path and data type.
 * @param rowData - The data object for the current row from which to extract and format the value.
 * @returns The formatted cell value as a string, or null if the original value is undefined.
 */
function getCellValue(
  columnSetting: ColumnSetting,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  rowData: any,
): string | React.JSX.Element | null {
  if (columnSetting.dataType === CellDataType.CUSTOM) {
    return columnSetting?.customComponent
      ? columnSetting.customComponent({ rowData: rowData })
      : null;
  }

  const extractedValue = extractDataFromRecord(
    rowData,
    columnSetting.fieldPath,
  );

  // Handle error in dotNotationToValue function
  if (extractedValue === undefined) {
    return null;
  }

  if (columnSetting.dataType === CellDataType.DATE) {
    return formatDate(extractedValue, false);
  } else if (columnSetting.dataType === CellDataType.DATE_RELATIVE) {
    return formatDate(extractedValue, true);
  } else if (columnSetting.dataType === CellDataType.NUMBER) {
    return formatNumber(extractedValue, columnSetting.noDecimal ?? 1, false);
  } else if (columnSetting.dataType === CellDataType.PER_CENT) {
    return formatNumber(extractedValue, columnSetting.noDecimal ?? 1, true);
  }

  return extractedValue;
}

interface TableHeaderCellProps {
  columnSetting: ColumnSetting;
}

/**
 * Renders a table header cell based on the provided column setting.
 * @param props The properties for the table header cell, including the column setting.
 * @param props.columnSetting The settings for the column, including the header name and alignment.
 * @returns The table header cell.
 */
function TableHeaderCell({
  columnSetting,
}: TableHeaderCellProps): React.JSX.Element {
  return (
    <TableCell key={`${columnSetting.fieldPath}-${columnSetting.headerName}`}>
      <Box
        display="flex"
        alignItems="center"
        justifyContent={
          columnSetting.align === "right"
            ? "flex-end"
            : columnSetting.align === "center"
              ? "center"
              : "flex-start"
        }
      >
        {columnSetting.description && (
          <Tooltip title={columnSetting.description}>
            <HelpOutline sx={{ fontSize: "18px", marginRight: "3px" }} />
          </Tooltip>
        )}
        {columnSetting.headerName}
      </Box>
    </TableCell>
  );
}

/**
 * Renders a basic table component using Material-UI components.
 *
 * This component takes in data and column settings to dynamically generate a table.
 * Each column can be customized with a header name and alignment, while the data
 * is passed as an array of objects where each object represents a row in the table.
 * @param props - The component props.
 * @param props.data - The data to be displayed in the table. Each object in the array represents a row.
 * @param props.columnSettings - Settings for each column in the table, including the header name and alignment.
 * @returns The table component as a JSX element.
 */
export default function BasicTable({
  data,
  columnSettings,
}: BasicTableProps): React.JSX.Element | null {
  if (data === undefined) {
    return null;
  }

  const sums = columnSettings.reduce<Record<string, number>>(
    (acc, columnSetting) => {
      if (columnSetting.showSubtotal) {
        acc[columnSetting.fieldPath] = data.reduce((sum, record) => {
          const value = extractDataFromRecord(record, columnSetting.fieldPath);
          return sum + (typeof value === "number" ? value : 0); // Ensure value is a number
        }, 0);
      }
      return acc;
    },
    {},
  );

  const showTableFooter = columnSettings.some(
    (columnSetting) => columnSetting.showSubtotal,
  );

  return (
    <TableContainer component={Paper} style={{ maxHeight: "100vh" }}>
      <Table stickyHeader>
        <TableHead>
          <TableRow key={"header"}>
            {columnSettings.map((columnSetting, index) => (
              <TableHeaderCell
                key={`header-${index}`}
                columnSetting={columnSetting}
              />
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map((row, index) => (
            <TableRow key={index}>
              {columnSettings.map((columnSetting, cellIndex) => (
                <TableCell
                  key={`${index}-${cellIndex}`}
                  align={columnSetting.align}
                >
                  {getCellValue(columnSetting, row)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
        {showTableFooter && (
          <TableFooter>
            <TableRow key={"footer"}>
              {columnSettings.map((columnSetting, index) => (
                <TableCell key={`footer-${index}`} align={columnSetting.align}>
                  {index === 0
                    ? "Total"
                    : columnSetting.showSubtotal
                      ? formatNumber(sums[columnSetting.fieldPath], 0, false)
                      : null}
                </TableCell>
              ))}
            </TableRow>
          </TableFooter>
        )}
      </Table>
    </TableContainer>
  );
}
