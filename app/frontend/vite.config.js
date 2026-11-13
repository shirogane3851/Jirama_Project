import react from '@vitejs/plugin-react'
import legacy from '@vitejs/plugin-legacy'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    react(),
    legacy({
      targets: ['chrome >= 49', 'android >= 5', 'ios >= 11'],
      renderModernChunks: false,
    }),
  ],
  build: {
    cssTarget: ['chrome61', 'safari12'],
  },
})