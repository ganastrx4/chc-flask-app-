import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/chc-flask-app-/', // 👈 importante
  plugins: [react()],
})
