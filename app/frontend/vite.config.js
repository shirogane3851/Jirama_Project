import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  build: {
    cssTarget: ['chrome61', 'safari12'],
  },
})