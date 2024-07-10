import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";

// Use 'Element | null' as the type for rootElement since document.getElementById can return null
const rootElement: Element | null = document.getElementById("root");

if (rootElement !== null) {
  const root: ReactDOM.Root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
