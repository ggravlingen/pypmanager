import { Box } from "@mui/material";
import { NavigationBar, TableGeneralLedger } from "./components";
import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";

export default function MainLayout() {
  return (
    <HashRouter>
      <Box sx={{ display: "flex" }}>
        <NavigationBar />
        <Box style={{ flexGrow: 1 }}>
          <Routes>
            <Route path="/" element={<TableGeneralLedger />} />
          </Routes>
        </Box>
      </Box>
    </HashRouter>
  );
}