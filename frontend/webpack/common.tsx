import Dotenv from "dotenv-webpack";
import webpack from "webpack"; // to access built-in plugins

const commonConfig: webpack.Configuration = {
  entry: ["./src/index.tsx"],
  resolve: {
    alias: {},
    // Keep js-files here to load node-modules properly
    extensions: [".js", ".tsx", ".ts", ".jsx", ".mjs"],
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "ts-loader",
        },
      },
    ],
  },
  plugins: [
    new webpack.ProgressPlugin(),
    new Dotenv({
      path: "./.env",
      safe: true,
      systemvars: true,
      silent: false,
      defaults: false,
    }),
  ],
};

export default commonConfig;
