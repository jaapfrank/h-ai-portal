/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hoeflon': {
          // Authentic Hoeflon brand colors based on logo
          25: '#fefefe',   // Pure white
          50: '#f9f9f9',   // Very light gray
          100: '#f4f4f4',  // Light gray
          200: '#e5e5e5',  // Light gray
          300: '#d4d4d4',  // Medium gray
          400: '#a3a3a3',  // Gray
          500: '#737373',  // Main gray
          600: '#525252',  // Dark gray
          700: '#404040',  // Darker gray
          800: '#262626',  // Very dark gray - HOEFLON BLACK
          900: '#171717',  // True black - MAIN HOEFLON COLOR
          // Authentic Hoeflon accent colors
          'red': '#dc2626',        // HOEFLON SIGNATURE RED (from logo)
          'red-light': '#fca5a5',  // Light red
          'red-dark': '#991b1b',   // Dark red
          'black': '#171717',      // Hoeflon black
          'gray': '#525252',       // Professional gray
        },
        // Industrial/Technical color palette
        'industrial': {
          'steel': '#64748b',
          'iron': '#475569', 
          'charcoal': '#334155',
          'carbon': '#1e293b',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'display': ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      boxShadow: {
        'hoeflon': '0 4px 6px -1px rgba(71, 85, 105, 0.1), 0 2px 4px -1px rgba(71, 85, 105, 0.06)',
        'hoeflon-lg': '0 10px 15px -3px rgba(71, 85, 105, 0.1), 0 4px 6px -2px rgba(71, 85, 105, 0.05)',
      }
    },
  },
  plugins: [],
}