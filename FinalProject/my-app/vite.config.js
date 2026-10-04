import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      // Uploaded images/videos are served by Flask; proxying them keeps
      // media URLs relative, exactly like behind nginx in Docker/production.
      '/static': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
