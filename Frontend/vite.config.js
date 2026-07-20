import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/locations': 'http://localhost:8000',
      '/crops': 'http://localhost:8000',
      '/advisory': 'http://localhost:8000',
      '/rules': 'http://localhost:8000',
      '/post-harvest': 'http://localhost:8000',
      '/api': 'http://localhost:8000',
    },
  },
})