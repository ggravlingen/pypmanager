import { ThemeProvider } from "@mui/material";
import { StandardTheme } from "@Theme";
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";

// Use 'Element | null' as the type for rootElement since document.getElementById can return null
const rootElement: Element | null = document.getElementById("root");

if (rootElement !== null) {
  // Correctly typed usage of ReactDOM.createRoot according to React 18+ type definitions
  const root: ReactDOM.Root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <ThemeProvider theme={StandardTheme("light")}>
        <App />
      </ThemeProvider>
    </React.StrictMode>,
  );
}
