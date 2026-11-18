/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sentinel: {
          dark: '#0a0f1d',
          card: '#111827',
          border: '#1f2937',
          primary: '#6366f1',
          accent: '#38bdf8'
        }
      }
    },
  },
  plugins: [],
}
