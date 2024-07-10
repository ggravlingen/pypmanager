import { createTheme, PaletteMode, Theme } from "@mui/material";

import { DarkPalette, LightPalette } from "./Palette";

const cellPadding = {
  paddingTop: "2px",
  paddingBottom: "2px",
  paddingLeft: "6px",
  paddingRight: "6px",
};

enum FontSize {
  TOOLTIP = "14px",
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
              backgroundColor: Palette.background.default,
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
            backgroundColor: Palette.primary.main,
            color: Palette.primary.contrastText,
          },
          footer: {
            fontSize: FontSize.TABLE_CELL,
            backgroundColor: Palette.background.paper,
            color: Palette.text.primary,
            borderTop: `1px solid ${Palette.primary.main}`,
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            fontSize: FontSize.TOOLTIP,
            backgroundColor: Palette.primary.main,
            color: Palette.primary.contrastText,
          },
        },
      },
    },
  };

  return createTheme(updatedTheme) as Theme;
};

export default StandardTheme;
