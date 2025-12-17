import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
        // Critical: Forward cookies for session management
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Forward cookies from browser to backend
            if (req.headers.cookie) {
              proxyReq.setHeader('Cookie', req.headers.cookie);
            }
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            // Forward Set-Cookie headers from backend to browser
            if (proxyRes.headers['set-cookie']) {
              // Ensure cookies work for localhost
              const cookies = proxyRes.headers['set-cookie'].map(cookie => {
                return cookie
                  .replace(/Domain=[^;]+;?/gi, '')
                  .replace(/Secure;?/gi, '')
                  .replace(/SameSite=None/gi, 'SameSite=Lax');
              });
              proxyRes.headers['set-cookie'] = cookies;
            }
          });
        }
      }
    }
  }
})

