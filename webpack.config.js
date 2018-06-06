var autoprefixer = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var FaviconsWebpackPlugin = require('favicons-webpack-plugin');
var path = require('path');
var webpack = require('webpack');

var resolve = path.resolve.bind(path, __dirname);

var extractTextPlugin;
var fileLoaderPath;
var output;

if (process.env.NODE_ENV === 'production') {
  output = {
    path: resolve('saleor/static/assets/'),
    filename: '[name].[chunkhash].js',
    publicPath: 'https://saleor-demo.s3.amazonaws.com/assets/'
  };
  fileLoaderPath = 'file?name=[name].[hash].[ext]';
  extractTextPlugin = new ExtractTextPlugin('[name].[contenthash].css');
} else {
  output = {
    path: resolve('saleor/static/assets/'),
    filename: '[name].js',
    publicPath: '/static/assets/'
  };
  fileLoaderPath = 'file?name=[name].[ext]';
  extractTextPlugin = new ExtractTextPlugin('[name].css');
}

var bundleTrackerPlugin = new BundleTracker({
  filename: 'webpack-bundle.json'
});

var commonsChunkPlugin = new webpack.optimize.CommonsChunkPlugin({
  names: 'vendor'
});

var occurenceOrderPlugin = new webpack.optimize.OccurenceOrderPlugin();

var environmentPlugin = new webpack.DefinePlugin({
  'process.env': {
    NODE_ENV: JSON.stringify(process.env.NODE_ENV || 'development')
  }
});

var providePlugin = new webpack.ProvidePlugin({
  $: 'jquery',
  '_': 'underscore',
  jQuery: 'jquery',
  'window.jQuery': 'jquery',
  'Tether': 'tether',
  'window.Tether': 'tether'
});

var faviconsWebpackPlugin = new FaviconsWebpackPlugin({
  logo: './saleor/static/images/favicon.svg',
  prefix: 'favicons/',
  title: "Saleor"
});

var config = {
  entry: {
    
    category: './saleor/static/js/category.js',
    dashboard: './saleor/static/dashboard/js/dashboard.js',
    storefront: './saleor/static/js/storefront.js',
    kitchen_transfer: './saleor/static/backend/js/kitchen_transfer/create/index.js',
    menu_transfer: './saleor/static/backend/js/menu_transfer/create/index.js',
    transfer: './saleor/static/backend/js/transfer/create/index.js',
    transfer_close: './saleor/static/backend/js/transfer_close/list/index.js',
    kitchen_transfer_close: './saleor/static/backend/js/kitchen_transfer_close/list/index.js',
    menu_transfer_close: './saleor/static/backend/js/menu_transfer_close/list/index.js',
    transfer_list: './saleor/static/backend/js/transfer/list/index.js',
    menu_transfer_list: './saleor/static/backend/js/menu_transfer/list/index.js',
    kitchen_transfer_list: './saleor/static/backend/js/kitchen_transfer/list/index.js',
    transferred_items_close: './saleor/static/backend/js/transfer_close/items/index.js',
    kitchen_transferred_items_close: './saleor/static/backend/js/kitchen_transfer_close/items/index.js',
    menu_transferred_items_close: './saleor/static/backend/js/menu_transfer_close/items/index.js',
    kitchen_transferred_items_close_view: './saleor/static/backend/js/kitchen_transfer_close/items_view/index.js',
    menu_transferred_items_close_view: './saleor/static/backend/js/menu_transfer_close/items_view/index.js',
    transferred_items_close_view: './saleor/static/backend/js/transfer_close/items_view/index.js',
    transferred_items: './saleor/static/backend/js/transfer/items/index.js',
    kitchen_transferred_items: './saleor/static/backend/js/kitchen_transfer/items/index.js',
    menu_transferred_items: './saleor/static/backend/js/menu_transfer/items/index.js',
    transferred_items_view: './saleor/static/backend/js/transfer/items_view/index.js',
    kitchen_transferred_items_view: './saleor/static/backend/js/kitchen_transfer/items_view/index.js',
    menu_transferred_items_view: './saleor/static/backend/js/menu_transfer/items_view/index.js',
    menu: './saleor/static/backend/js/menu/list/index.js',
    vendor: [
      'babel-es6-polyfill',
      'bootstrap',
      'jquery',
      'jquery.cookie',
      'react',
      'react-relay',      
    ]
  },
  output: output,
  module: {
    loaders: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel'
      },
      {
        test: /\.json$/,
        loader: 'json'
      },
      {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract([
          'css?sourceMap',
          'postcss',
          'sass'
        ])
      }, { test: /\.css$/, loader: "style-loader!css-loader" },
      {
        test: /\.(eot|otf|png|svg|jpg|ttf|woff|woff2)(\?v=[0-9.]+)?$/,
        loader: fileLoaderPath,
        include: [
          resolve('node_modules'),
          resolve('saleor/static/fonts'),
          resolve('saleor/static/images'),
          resolve('saleor/static/dashboard/images')
        ]
      }
    ]
  },
  plugins: [
    bundleTrackerPlugin,
    commonsChunkPlugin,
    environmentPlugin,
    extractTextPlugin,
    occurenceOrderPlugin,
    providePlugin,
    faviconsWebpackPlugin
  ],
  postcss: function() {
    return [autoprefixer];
  },
  resolve: {
    alias: {
      'jquery': resolve('node_modules/jquery/dist/jquery.js'),
      'react': resolve('node_modules/react/dist/react.min.js'),
      'react-dom': resolve('node_modules/react-dom/dist/react-dom.min.js')
    },
    modulesDirectories: [
          'node_modules'
    ]
  },
  sassLoader: {
    sourceMap: true
  }
};

module.exports = config;
