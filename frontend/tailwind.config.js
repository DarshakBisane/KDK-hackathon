/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F7F8FC",
        "bg-secondary": "#F1F3FA",
        card: "#FFFFFF",
        lavender: {
          light: "#EEEAFE",
          DEFAULT: "#EEEAFE",
          text: "#5845D8",
          dark: "#4334A6",
        },
        paleblue: {
          light: "#EAF2FF",
          DEFAULT: "#EAF2FF",
          text: "#2563EB",
        },
        mint: {
          light: "#EAF8F1",
          DEFAULT: "#EAF8F1",
          text: "#1E824C",
        },
        brand: {
          DEFAULT: "#6C63FF",
          hover: "#5A52E0",
          light: "#F0EFFF",
        },
        text: {
          primary: "#172033",
          secondary: "#667085",
          muted: "#98A2B3",
        },
        border: {
          subtle: "#E4E7EC",
          hover: "#D0D5DD",
        },
        status: {
          success: "#35A76F",
          warning: "#E7A83B",
          danger: "#E35D6A",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 10px rgba(23, 32, 51, 0.04), 0 1px 3px rgba(23, 32, 51, 0.02)',
        'soft-md': '0 6px 20px rgba(23, 32, 51, 0.06), 0 2px 6px rgba(23, 32, 51, 0.03)',
        'soft-lg': '0 12px 32px rgba(23, 32, 51, 0.08), 0 4px 12px rgba(23, 32, 51, 0.04)',
        'nav': '0 4px 20px rgba(23, 32, 51, 0.05)',
      },
      borderRadius: {
        'xl': '14px',
        '2xl': '18px',
        '3xl': '24px',
      }
    },
  },
  plugins: [],
}
