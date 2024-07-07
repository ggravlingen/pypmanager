import { merge } from "webpack-merge";
import * as path from "path";
import commonConfig from "./common";

export default merge(commonConfig, {
  mode: "development",
  output: {
    path: path.join(__dirname, "..", "static"),
    filename: "main.js",
  },
  devtool: "inline-source-map",
  watch: true,
  watchOptions: {
    aggregateTimeout: 1000,
    ignored: /node_modules/,
  },
});
