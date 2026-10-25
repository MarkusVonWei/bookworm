import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  plugins: [uni()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://www.bookworm.icu',
        changeOrigin: true
      },
      '/data': {
        target: 'https://www.bookworm.icu',
        changeOrigin: true
      }
    }
  }
})
