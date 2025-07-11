import * as path from "path";
import TerserPlugin from "terser-webpack-plugin";
import { merge } from "webpack-merge";

import commonConfig from "./common";

export default merge(commonConfig, {
  mode: "production",
  output: {
    path: path.join(__dirname, "..", "static"),
    publicPath: "static/",
    filename: "[name].[contenthash].js",
    chunkFilename: "[name].[contenthash].js",
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: { drop_console: true },
          format: { comments: false },
        },
        extractComments: false,
      }),
    ],
    splitChunks: {
      chunks: "all", // Split all chunks, including async and non-async ones
      minSize: 20000, // Minimum size (in bytes) for a chunk to be generated
      maxSize: 250000, // Try to split chunks into sizes below 250 KB
      minChunks: 1, // Minimum number of chunks that must share a module before splitting
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/, // Split vendor libraries (e.g., React, Lodash) into a separate chunk
          name: "vendors",
          priority: -10,
        },
        default: {
          minChunks: 2, // Split modules shared by at least 2 chunks
          priority: -20,
          reuseExistingChunk: true, // Reuse existing chunks instead of creating duplicates
        },
      },
    },
  },
  performance: {
    hints: false,
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
});
