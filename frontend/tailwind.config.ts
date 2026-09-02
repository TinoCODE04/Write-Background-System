import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17221d",
        fog: "#f3f5f1",
        moss: "#2f6b4f",
        lime: "#c9f45b",
        sand: "#e7e4da"
      },
      boxShadow: {
        soft: "0 18px 60px rgba(32, 46, 38, 0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;

