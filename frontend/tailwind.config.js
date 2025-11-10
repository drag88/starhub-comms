/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f5ed',   // Lightest StarHub Green
          100: '#ccebdb',
          200: '#99d7b7',
          300: '#66c393',
          400: '#33af6f',
          500: '#00A651',  // StarHub Green (main brand color)
          600: '#008541',  // Darker shade for hover states
          700: '#006431',  // Even darker
          800: '#004220',  // Very dark
          900: '#002110',  // Darkest
        },
        success: '#00A651', // StarHub Green
        warning: '#f59e0b',
        danger: '#ef4444',
      }
    },
  },
  plugins: [],
}
