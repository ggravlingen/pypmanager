/* eslint-disable */
const express = require("express");
const path = require("path");
const http = require("http");

// Paths
const FRONTEND_DIR = path.join(__dirname, "../");
const TEMPLATE_DIR = path.join(FRONTEND_DIR, "templates");
const STATIC_DIR = path.join(FRONTEND_DIR, "static");

const app = express();
const server = http.createServer(app);

// Middleware for logging requests
app.use((req, res, next) => {
  console.log(
    `${new Date().toISOString()} - ${req.method} request to ${req.url}`,
  );
  next(); // Continue to the next middleware or route handler
});

// Serving the files in the static folder
app.use("/static", express.static(STATIC_DIR));

app.get("/", (req, res) => {
  res.sendFile(path.join(TEMPLATE_DIR, "index.html"), (e) => {
    if (error) {
      console.error("Error sending file:", error);
    }
  });
});

server.listen(3000, () => {
  console.log("A simple server is running on port 3000");
});
