import typography from '@tailwindcss/typography'
import animate from 'tailwindcss-animate'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
      extend: {
          colors: {
              background: "#09090B",
              foreground: "#FAFAFA",
              secondary: "#111113",
              "secondary-foreground": "#FAFAFA",
              card: "#17171A",
              "card-foreground": "#FAFAFA",
              popover: "#17171A",
              "popover-foreground": "#FAFAFA",
              muted: "#111113",
              "muted-foreground": "#A1A1AA",
              border: "rgba(255,255,255,0.08)",
              input: "rgba(255,255,255,0.08)",
              ring: "#3B82F6",
              accent: "#3B82F6",
              "accent-foreground": "#FAFAFA",
              primary: "#FAFAFA",
              "primary-foreground": "#09090B",
              destructive: "#EF4444",
              "destructive-foreground": "#FAFAFA",
              "medical-green": "#10B981"
          },
          borderRadius: {
              DEFAULT: "0.25rem",
              sm: "0.125rem",
              md: "0.375rem",
              lg: "0.5rem",
              xl: "0.75rem",
              "2xl": "1rem",
              "3xl": "1.5rem", /* 24px */
              "4xl": "2rem",
              full: "9999px"
          },
          spacing: {
              "margin-mobile": "16px",
              "stack-lg": "32px",
              "stack-md": "16px",
              "gutter": "24px",
              "margin-desktop": "40px",
              "stack-sm": "8px",
              "unit": "4px",
              "container-max": "1440px"
          },
          fontFamily: {
              sans: ["Inter", "sans-serif"],
              mono: ["JetBrains Mono", "monospace"],
          }
      }
  },
  plugins: [animate, typography],
}
