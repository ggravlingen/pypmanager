import App from "./App";
import React from 'react';
import ReactDOM from 'react-dom';

const rootElement = document.getElementById('root');

if (rootElement) {
  const root = (ReactDOM as any).createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  console.error("Root element 'root' not found in the document.");
}
