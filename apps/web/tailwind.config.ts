import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f5f0e8",
        ink: "#163637",
        sea: "#86b7b6",
        pine: "#254b4b",
        mist: "#dbe7e4",
        coral: "#f4a98a",
        night: "#0f1c24"
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "ui-sans-serif", "system-ui"],
        display: ["'Fraunces'", "serif"]
      },
      boxShadow: {
        float: "0 18px 55px rgba(19, 55, 55, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;

