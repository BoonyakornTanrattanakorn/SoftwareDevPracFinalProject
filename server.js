const express = require("express");
const dotenv = require("dotenv");
const cookieParser = require("cookie-parser");
const cors = require("cors");
const connectDB = require("./config/db");

// Load env vars
dotenv.config({ path: "./config/config.env" });

// routes
const coworkingspaces = require("./routes/coworkingspaces");
const reservations = require("./routes/reservations");
const auth = require("./routes/auth");

// Connect DB
connectDB();

const app = express();
// // Enable CORS
// app.use(cors());
// // Query Parser
// app.set("query parser", "extended");
// // Body parser
// app.use(express.json());
// // Handle invalid JSON body format
// app.use((err, req, res, next) => {
//   if (err instanceof SyntaxError && err.status === 400 && "body" in err) {
//     return res
//       .status(400)
//       .json({ success: false, message: "Invalid JSON payload" });
//   }
//   next(err);
// });
// // Cookie parser
// app.use(cookieParser());

// // Mount routers
// app.use("/api/v1/coworkingspaces", coworkingspaces);
// app.use("/api/v1/reservations", reservations);
// app.use("/api/v1/auth", auth);

const PORT = process.env.PORT || 5000;

const server = app.listen(
  PORT,
  console.log("Server running in", process.env.NODE_ENV, "mode on port", PORT),
);

process.on("unhandledRejection", (err, promise) => {
  console.log(`Error: ${err.message}`);
  server.close(() => process.exit(1));
});
