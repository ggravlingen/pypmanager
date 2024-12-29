import { Box, PaletteMode } from "@mui/material";
import { CssBaseline, ThemeProvider } from "@mui/material";
import { StandardTheme } from "@Theme";
import React from "react";
import { HashRouter, Route, Routes } from "react-router-dom";

import {
  ChartPriceHistoryWrapper,
  NavigationBar,
  TableAllTransaction,
  TableCurrentPortfolio,
  TableGeneralLedger,
  TableHistoricalPortfolio,
  TableIncomeStatement,
  TableMarketDataOverview,
} from "./components";

interface RouteListProps {
  path: string;
  element: React.ReactElement;
}

const ROUTE_LIST: RouteListProps[] = [
  {
    path: "/",
    element: <TableCurrentPortfolio />,
  },
  {
    path: "/history",
    element: <TableHistoricalPortfolio />,
  },
  {
    path: "/income_statement",
    element: <TableIncomeStatement />,
  },
  {
    path: "/ledger",
    element: <TableGeneralLedger />,
  },
  {
    path: "/marketDataOverview",
    element: <TableMarketDataOverview />,
  },
  {
    path: "/transaction",
    element: <TableAllTransaction />,
  },
  {
    path: "/chart/:isinCode",
    element: <ChartPriceHistoryWrapper />,
  },
];

/**
 * MainLayout component that defines the main structure of the application.
 * It sets up a HashRouter for navigation, a NavigationBar for navigating between pages,
 * and a main content area where different components are rendered based on the current route.
 *
 * Currently, it only includes a single route that renders the TableGeneralLedger component
 * at the root path ("/"). The layout uses a flexbox design to ensure that the NavigationBar
 * and the content area are properly aligned and sized.
 * @returns The MainLayout component, comprising the HashRouter, NavigationBar,
 * and the main content area with defined routes.
 */
export default function MainLayout() {
  // Fetch color mode from the local storage
  const storedColorMode = localStorage.getItem("colorMode") as PaletteMode;

  const [colorMode, setColorMode] = React.useState<PaletteMode>(
    storedColorMode || "light",
  );

  return (
    <ThemeProvider theme={StandardTheme(colorMode)}>
      <CssBaseline />
      <HashRouter>
        <Box sx={{ display: "flex" }}>
          <NavigationBar colorMode={colorMode} setColorMode={setColorMode} />
          <Box style={{ flexGrow: 1, maxWidth: "95%" }}>
            <Routes>
              {ROUTE_LIST.map(({ path, element }) => (
                <Route key={path} path={path} element={element} />
              ))}
            </Routes>
          </Box>
        </Box>
      </HashRouter>
    </ThemeProvider>
  );
}
