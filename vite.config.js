import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync } from 'fs'
import { join } from 'path'

export default defineConfig({
  plugins: [
    react(),
    // Copy _redirects file to dist during build
    {
      name: 'copy-redirects',
      closeBundle() {
        const src = join(process.cwd(), 'public', '_redirects')
        const dest = join(process.cwd(), 'dist', '_redirects')
        try {
          copyFileSync(src, dest)
          console.log('✅ Copied _redirects to dist')
        } catch (err) {
          console.warn('⚠️ Could not copy _redirects:', err.message)
        }
      }
    }
  ],
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

