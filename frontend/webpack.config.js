const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/index.tsx', // Entry point of your React application
  output: {
    path: path.resolve(__dirname, 'static'), // Output directory
    filename: 'main.js', // Output filename
  },
  devtool: 'inline-source-map', // Optional: Add source maps for debugging
  resolve: {
    extensions: ['.tsx'], // Resolve these file extensions
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'ts-loader',
        },
      },
    ],
  },
  plugins: [],
};
