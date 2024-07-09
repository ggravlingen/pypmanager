import { Box } from "@mui/material";
import { NavigationBar, TableGeneralLedger } from "./components";
import React from "react";

export default function MainLayout() {
  return (
    <Box sx={{ display: "flex" }}>
      <NavigationBar />
      <Box style={{ flexGrow: 1 }}>
        <TableGeneralLedger />
      </Box>
    </Box>
  );
}
