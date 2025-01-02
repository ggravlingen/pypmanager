import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import http from "http";
import RateLimit from "express-rate-limit";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const FRONTEND_DIR = path.join(__dirname, "../");
const TEMPLATE_DIR = path.join(FRONTEND_DIR, "templates");
const STATIC_DIR = path.join(FRONTEND_DIR, "static");

console.log("Serving files from:");
console.log(FRONTEND_DIR);
console.log(TEMPLATE_DIR);
console.log(STATIC_DIR);
console.log("---");

const app = express();
const server = http.createServer(app);

// set up rate limiter: maximum of 100 requests per 15 minutes
const limiter = RateLimit({
  windowMs: 1 * 60 * 1000, // 1 minutes
  max: 1000, // max 1000 requests per windowMs
});

// apply rate limiter to all requests
app.use(limiter);

// Serving the files in the static folder
app.use("/static", express.static(STATIC_DIR));

// Middleware for logging requests
app.use((req, res, next) => {
  console.log(
    `${new Date().toISOString()} - ${req.method} request to ${req.url}`,
  );
  next(); // Continue to the next middleware or route handler
});

app.get("/", (req, res) => {
  res.sendFile(path.join(TEMPLATE_DIR, "index.html"), (error) => {
    if (error) {
      console.error("Error sending file:", error);
    }
  });
});

server.listen(3000, () => {
  console.log("A simple server is running on port 3000");
});
