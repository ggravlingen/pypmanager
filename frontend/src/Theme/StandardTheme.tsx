import { createTheme } from "@mui/material/styles";

const StandardTheme = createTheme({
  components: {
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: "#000000",
          ".MuiTableCell-root": {
            color: "#ffffff",
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          fontSize: "12px",
          paddingTop: "6px",
          paddingBottom: "6px",
          paddingLeft: "6px",
          paddingRight: "6px",
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          "&:not(.MuiTableHead-root) > &:nth-of-type(odd)": {
            backgroundColor: "#f9f9f9",
          },
        },
      },
    },
  },
});

export default StandardTheme;
