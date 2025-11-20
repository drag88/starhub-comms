/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        obsidian: '#050505',
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
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
      },
      boxShadow: {
        'glow': '0 0 20px rgba(0, 166, 81, 0.3)',
        'glow-lg': '0 0 30px rgba(0, 166, 81, 0.5)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow': 'conic-gradient(from 90deg at 50% 50%, #00000000 50%, #00A651 100%)',
      }
    },
  },
  plugins: [],
}
