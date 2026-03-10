import { type Config } from 'tailwindcss';

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--color-background)",
        foreground: "var(--color-foreground)",
        primary: "var(--color-primary)",
        accent: "var(--color-accent)",
        card: "var(--color-card)",
        muted: "var(--color-muted)",
        border: "var(--color-border)",
        success: "var(--color-success)",
        warning: "var(--color-warning)"
      },
      borderRadius: {
        DEFAULT: "var(--radius)"
      },
      boxShadow: {
        DEFAULT: "var(--shadow)"
      }
    }
  },
  plugins: []
};

export default config;