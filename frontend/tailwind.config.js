/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        accent: '#560ea0',
        'accent-dark': '#1a0133',
      },
    },
  },
  plugins: [require('tailwindcss-primeui')],
}
