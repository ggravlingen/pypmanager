import App from "./App";
import React from "react";
import ReactDOM from "react-dom/client";

// Use 'Element | null' as the type for rootElement since document.getElementById can return null
const rootElement: Element | null = document.getElementById("root");

if (rootElement !== null) {
  // Correctly typed usage of ReactDOM.createRoot according to React 18+ type definitions
  const root: ReactDOM.Root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
