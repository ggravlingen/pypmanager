import { createTheme, PaletteMode, Theme } from "@mui/material";

import { DarkPalette, LightPalette } from "./Palette";

const cellPadding = {
  paddingTop: "2px",
  paddingBottom: "2px",
  paddingLeft: "6px",
  paddingRight: "6px",
};

enum FontSize {
  TABLE_CELL = "12px",
}

const StandardTheme = (mode: PaletteMode) => {
  const Palette = mode === "dark" ? DarkPalette : LightPalette;

  const updatedTheme = {
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
            fontWeight: "bold",
            backgroundColor: Palette.common.black,
            color: Palette.common.white,
          },
        },
      },
    },
  };

  return createTheme(updatedTheme) as Theme;
};

export default StandardTheme;
