/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      container: {
        center: true,
        padding: 0,
        screens: {
          sm: '640px',
          md: '640px',
          lg: '800px',
          xl: '800px',
          '2xl': '800px'
        }
      },
      animation: {
        'pulse-fast': 'pulse 1s linear infinite',
      },
      colors: {
        "background": "#ebeff3",
        "chat-1": "#1b5a9d",
        "chat-2": "#b54fa2",
        "clova-primary": "#05d686",
        "clova-service": "#06CC80",
        "clova-pointed": "#06CC80",
        "clova-blue": "#2284F5",
        "clova-gray": {
          100: "#F7F7F7",
          200: "#CCCCCC",
          300: "#BEBEBE",
          400: "#999999",
          500: "#666666",
          600: "#333333",
          700: "#000000"
        },
      }
    },
  },
  plugins: [],
}

