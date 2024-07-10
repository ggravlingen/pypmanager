import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TableRow,
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
  NUMBER = "number",
  PER_CENT = "per_cent",
  STRING = "string",
}

interface ColumnSetting {
  headerName: string;
  fieldPath: string;
  align: CellAlign;
  dataType: CellDataType;
  noDecimals?: number;
  showSubtotal?: boolean;
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
): string | null {
  const extractedValue = extractDataFromRecord(
    rowData,
    columnSetting.fieldPath,
  );

  // Handle error in dotNotationToValue function
  if (extractedValue === undefined) {
    return null;
  }

  if (columnSetting.dataType === CellDataType.DATE) {
    return formatDate(extractedValue);
  } else if (columnSetting.dataType === CellDataType.NUMBER) {
    return formatNumber(extractedValue, columnSetting.noDecimals ?? 1, false);
  } else if (columnSetting.dataType === CellDataType.PER_CENT) {
    return formatNumber(extractedValue, columnSetting.noDecimals ?? 1, true);
  }

  return extractedValue;
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
}: BasicTableProps): JSX.Element | null {
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
          <TableRow>
            {columnSettings.map((columnSetting) => (
              <TableCell
                key={columnSetting.fieldPath}
                align={columnSetting.align || "left"}
              >
                {columnSetting.headerName}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data?.map((row, index) => (
            <TableRow key={index}>
              {columnSettings.map((columnSetting) => (
                <TableCell
                  key={columnSetting.fieldPath}
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
            <TableRow>
              {columnSettings.map((columnSetting, index) => (
                <TableCell
                  key={columnSetting.fieldPath}
                  align={columnSetting.align}
                >
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
