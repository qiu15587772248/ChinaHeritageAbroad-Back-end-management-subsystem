module.exports = {
  devServer: {
    port: 8081,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: false
      }
    }
  },
  lintOnSave: false
} 