import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#eef5ff",
          100: "#d9eaff",
          600: "#135fbf",
          700: "#114b96",
          800: "#123e78",
          900: "#0d2a52",
          950: "#071a35"
        },
        mint: {
          50: "#edfcf5",
          500: "#18a76f",
          600: "#0d8759"
        }
      },
      boxShadow: {
        card: "0 18px 50px -28px rgba(7, 26, 53, 0.28)"
      }
    }
  },
  plugins: []
};

export default config;

