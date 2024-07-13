import path from "path";
import { merge } from "webpack-merge";

import commonConfig from "./common";

export default merge(commonConfig, {
  entry: path.resolve(__dirname, "../src/index.tsx"),
  mode: "development",
  output: {
    clean: true,
    path: path.resolve(__dirname, "../", "static"),
    filename: "main.js",
  },
});
