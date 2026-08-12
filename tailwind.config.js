/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        navy: "#1E3A5F",
        teal: "#00E5B0",
        purple: "#5B3FF8",
        coral: "#FF7E67",
        slate: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'premium': '0 20px 50px -12px rgba(15, 23, 42, 0.1)',
      }
    },
  },
  plugins: [],
}
