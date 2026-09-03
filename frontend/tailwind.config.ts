import type { Config } from "tailwindcss";

// All semantic colors are driven by CSS variables so the UI can switch between
// light, dark, and user-defined custom themes at runtime.
const variable = (name: string) => `rgb(var(--${name}) / <alpha-value>)`;

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: variable("ink"),
        fog: variable("fog"),
        moss: variable("brand"),
        lime: variable("accent"),
        sand: "#e7e4da",
        // "black" is the themed foreground ink, "white" is the themed surface.
        black: variable("ink"),
        white: variable("surface")
      },
      boxShadow: {
        soft: "0 18px 60px rgba(32, 46, 38, 0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;