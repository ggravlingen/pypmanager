import { createTheme } from "@mui/material/styles";
import Palette from "./Palette";

const cellPadding = {
  paddingTop: "2px",
  paddingBottom: "2px",
  paddingLeft: "6px",
  paddingRight: "6px",
};

enum FontSize {
  TABLE_CELL = "12px",
}

const StandardTheme = createTheme({
  palette: Palette,
  components: {
    MuiTableRow: {
      styleOverrides: {
        root: {
          "&:nth-of-type(odd)": {
            backgroundColor: "#f9f9f9",
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          ...cellPadding,
          // Remove lines between rows
          borderBottom: "none !important",
          fontSize: FontSize.TABLE_CELL,
          "&:last-child": {
            ...cellPadding,
          },
        },
        head: {
          fontSize: FontSize.TABLE_CELL,
          backgroundColor: Palette.common.black,
          color: Palette.common.white,
        },
      },
    },
  },
});

export default StandardTheme;
