import Dotenv from "dotenv-webpack";
import path from "path";
import webpack from "webpack"; // to access built-in plugins

const commonConfig: webpack.Configuration = {
  context: path.resolve(__dirname, ".."),
  entry: ["./src/index.tsx"],
  resolve: {
    alias: {
      "@Api": path.resolve("src/Api"),
      "@ContextProvider": path.resolve("src/ContextProvider"),
      "@Generic": path.resolve("src/GenericComponents"),
      "@Theme": path.resolve("src/Theme"),
      "@Utils": path.resolve("src/Utils"),
    },
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
