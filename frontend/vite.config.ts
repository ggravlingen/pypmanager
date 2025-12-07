import react from "@vitejs/plugin-react";
import fs from "fs";
import path from "path";
import { defineConfig, type Plugin } from "vite";

/**
 * Plugin to move index.html from static/ to templates/ after build.
 * This matches the FastAPI backend's expectation of serving templates/index.html.
 */
function moveIndexHtmlPlugin(): Plugin {
  return {
    name: "move-index-html",
    closeBundle() {
      const src = path.resolve(__dirname, "static/index.html");
      const dest = path.resolve(__dirname, "templates/index.html");
      if (fs.existsSync(src)) {
        fs.copyFileSync(src, dest);
        fs.unlinkSync(src);
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), moveIndexHtmlPlugin()],
  base: "/static/",
  resolve: {
    alias: {
      "@Api": path.resolve(__dirname, "src/Api"),
      "@Const": path.resolve(__dirname, "src/Constant"),
      "@ContextProvider": path.resolve(__dirname, "src/ContextProvider"),
      "@Generic": path.resolve(__dirname, "src/GenericComponents"),
      "@Theme": path.resolve(__dirname, "src/Theme"),
      "@Utils": path.resolve(__dirname, "src/Utils"),
    },
  },
  build: {
    outDir: "static",
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, "index.html"),
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "react-router-dom"],
          mui: ["@mui/material", "@mui/icons-material"],
          apollo: ["@apollo/client", "graphql"],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/graphql": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
