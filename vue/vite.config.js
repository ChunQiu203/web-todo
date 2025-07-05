import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  devServer:{
    proxy:{
      '/api':{
        target: 'http://localhost:8000', // Flask server address
        changeOrigin: true,
        pathRewrite: {
          '^/api': '', // Remove /api prefix when forwarding to Flask
        }
      }
    }
  }
})
