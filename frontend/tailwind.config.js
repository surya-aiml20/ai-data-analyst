/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(214 18% 84%)",
        background: "hsl(40 23% 97%)",
        foreground: "hsl(222 30% 12%)",
        muted: "hsl(210 18% 94%)",
        primary: "hsl(174 72% 30%)",
        accent: "hsl(18 79% 55%)"
      }
    }
  },
  plugins: []
};
