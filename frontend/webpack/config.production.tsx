import * as path from "path";
import { merge } from "webpack-merge";

import commonConfig from "./common";

export default merge(commonConfig, {
  mode: "production",
  output: {
    path: path.join(__dirname, "..", "static"),
    filename: "main.js",
  },
  devtool: "source-map",
});
