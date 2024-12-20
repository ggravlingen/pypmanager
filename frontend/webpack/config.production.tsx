import HtmlWebpackPlugin from "html-webpack-plugin";
import * as path from "path";
import TerserPlugin from "terser-webpack-plugin";
import { merge } from "webpack-merge";

import commonConfig from "./common";

export default merge(commonConfig, {
  mode: "production",
  output: {
    path: path.join(__dirname, "..", "static"),
    filename: "[name].[contenthash].js",
    chunkFilename: "[name].[contenthash].js",
  },
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin({
      terserOptions: {
        compress: { drop_console: true },
        format: { comments: false },
      },
      extractComments: false,
    })],
    splitChunks: {
      chunks: "all",
      automaticNameDelimiter: "-",
    },
  },
  performance: {
    hints: false,
    maxEntrypointSize: 512000,
    maxAssetSize: 512000
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: path.join(__dirname, "..", "templates", "index_template.html"),
      filename: "./../templates/index.html",
    }),
  ],
});
