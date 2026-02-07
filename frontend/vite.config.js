import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  publicDir: 'public',
  server: {
    port: 5173,
    proxy: {
      // Proxy para desenvolvimento local
      // Quando VITE_API_URL não está definida, requisições para /api são redirecionadas para localhost:3000
      // Quando VITE_API_URL está definida, o axios usa a URL completa e ignora o proxy
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        secure: false, // Permitir HTTPS mesmo com certificado auto-assinado
        // Reescrever path se necessário (remover /api se o backend esperar sem)
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
