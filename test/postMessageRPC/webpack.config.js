const path = require('path');
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

module.exports = {
  mode: 'development',
  plugins: [
    new CleanWebpackPlugin(),
  ],
  entry: {
    index: './src/index.js',
    // worker: './src/worker.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'public/dist'),
  },
};