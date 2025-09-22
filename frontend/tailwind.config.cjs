/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6B21A8', // morado principal
          50: '#F6F0FB',
          100: '#F1E6FA',
          200: '#E3CCF6',
          300: '#D6B2F2',
          400: '#C97FF0',
          500: '#B84BE8',
          600: '#8C2DAE'
        },
        accent: {
          DEFAULT: '#16A34A', // verde acento
          600: '#16A34A'
        },
        theme: {
          dark: '#0B0B0B',
          light: '#FFFFFF'
        }
      }
    }
  },
  plugins: []
}
