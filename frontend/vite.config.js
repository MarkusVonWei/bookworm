import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        // target: 'http://localhost:8000',
        target: 'https://www.bookworm.icu',
        changeOrigin: true
      },
      '/data': {
        // target: 'http://localhost:8000',
        target: 'https://www.bookworm.icu',
        changeOrigin: true
      }
    }
  }
})
