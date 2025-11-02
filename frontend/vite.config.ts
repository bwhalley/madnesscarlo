import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    hmr: {
      clientPort: 81, // Match the external port
      host: 'madness.mtgwhales.com',
    },
    watch: {
      usePolling: true, // Needed for Docker
    },
    // Allow all hosts (we're behind nginx reverse proxy)
    allowedHosts: [
      'madness.mtgwhales.com',
      'localhost',
      '127.0.0.1',
    ],
  },
})

