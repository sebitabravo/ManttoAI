/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      // Tipografía Apple: Inter como alternativa web a SF Pro
      // Inter tiene optical sizing similar y características comparables
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          '"SF Pro Display"',
          '"SF Pro Text"',
          "system-ui",
          "sans-serif",
        ],
        display: [
          "Inter",
          "-apple-system",
          '"SF Pro Display"',
          "system-ui",
          "sans-serif",
        ],
      },
      // Paleta Apple: binaria con único acento azul
      colors: {
        // Superficies Apple
        apple: {
          black: "#000000",         // Hero backgrounds, immersive
          white: "#ffffff",         // Text on dark, button text
          gray: "#f5f5f7",          // Section backgrounds, cards
          "gray-dark": "#1d1d1f",   // Primary text on light bg
        },
        // Primary: Apple Blue — único acento cromático
        primary: {
          50: "#e8f4ff",
          100: "#d4ebff",
          200: "#b0daff",
          300: "#7ac2ff",
          400: "#3a9eff",
          500: "#0071e3",  // Apple Blue principal
          600: "#0066cc",  // Links on light bg
          700: "#0056b3",
          800: "#004999",
          900: "#003d80",
        },
        // Neutrales Apple (escala reducida, sin tintes)
        neutral: {
          50: "#fafafa",
          100: "#f5f5f7",   // Apple gray
          200: "#e8e8ed",
          300: "#d2d2d7",
          400: "#86868b",   // Secondary text
          500: "#6e6e73",
          600: "#1d1d1f",   // Primary text
          700: "#1d1d1f",
          800: "#000000",
          900: "#000000",
        },
        // Semánticos — versión Apple (más sutiles)
        success: {
          50: "#e8f8ee",
          100: "#d1f1dd",
          200: "#a3e3bb",
          300: "#75d599",
          400: "#47c777",
          500: "#34c759",  // Apple green
          600: "#2db14d",
          700: "#248f3e",
          800: "#1b6d2f",
          900: "#124b20",
        },
        warning: {
          50: "#fff8e6",
          100: "#fff0cc",
          200: "#ffe199",
          300: "#ffd266",
          400: "#ffc333",
          500: "#ff9500",  // Apple orange
          600: "#e68600",
          700: "#cc7600",
          800: "#b36600",
          900: "#995600",
        },
        danger: {
          50: "#ffebeb",
          100: "#ffd6d6",
          200: "#ffadad",
          300: "#ff8585",
          400: "#ff5c5c",
          500: "#ff3b30",  // Apple red
          600: "#e63529",
          700: "#cc2f24",
          800: "#b3291f",
          900: "#99231a",
        },
        info: {
          50: "#e5f6ff",
          100: "#ccedff",
          200: "#99daff",
          300: "#66c8ff",
          400: "#33b5ff",
          500: "#5ac8fa",  // Apple cyan
          600: "#4fb4e1",
          700: "#45a0c8",
          800: "#3a8caf",
          900: "#307896",
        },
      },
      // Border radius Apple
      borderRadius: {
        none: "0",
        micro: "5px",      // Chips, tags
        DEFAULT: "8px",    // Buttons, cards estándar
        comfortable: "11px", // Search inputs
        lg: "12px",        // Feature panels
        xl: "16px",        // Large cards
        pill: "980px",     // CTAs pill (Learn more, Shop)
        full: "9999px",    // Círculos
      },
      // Tipografía Apple: escala con negative letter-spacing
      fontSize: {
        // Escala Display (20px+)
        "display-hero": ["56px", { lineHeight: "1.07", letterSpacing: "-0.5px", fontWeight: "600" }],
        "display-lg": ["40px", { lineHeight: "1.10", letterSpacing: "-0.4px", fontWeight: "600" }],
        "display-md": ["28px", { lineHeight: "1.14", letterSpacing: "-0.28px", fontWeight: "400" }],
        "display-sm": ["21px", { lineHeight: "1.19", letterSpacing: "-0.21px", fontWeight: "400" }],
        // Escala Text (<20px)
        xl: ["1.25rem", { lineHeight: "1.47", letterSpacing: "-0.32px" }],
        lg: ["1.125rem", { lineHeight: "1.47", letterSpacing: "-0.29px" }],
        base: ["1.0625rem", { lineHeight: "1.47", letterSpacing: "-0.374px" }], // 17px Apple body
        sm: ["0.875rem", { lineHeight: "1.43", letterSpacing: "-0.224px" }],    // 14px
        xs: ["0.75rem", { lineHeight: "1.33", letterSpacing: "-0.12px" }],      // 12px
        micro: ["0.625rem", { lineHeight: "1.47", letterSpacing: "-0.08px" }],  // 10px
      },
      fontWeight: {
        light: "300",
        normal: "400",
        medium: "500",
        semibold: "600",
        bold: "700",
      },
      letterSpacing: {
        tighter: "-0.5px",
        tight: "-0.374px",
        normal: "-0.224px",
        wide: "0",
      },
      lineHeight: {
        none: "1",
        tight: "1.07",
        snug: "1.14",
        normal: "1.47",
        relaxed: "1.6",
      },
      // Sombras Apple: soft, diffused, minimal
      boxShadow: {
        none: "none",
        sm: "0 1px 2px rgba(0, 0, 0, 0.04)",
        DEFAULT: "0 2px 8px rgba(0, 0, 0, 0.08)",
        md: "0 4px 12px rgba(0, 0, 0, 0.1)",
        lg: "3px 5px 30px rgba(0, 0, 0, 0.12)",  // Apple product card shadow
        apple: "3px 5px 30px rgba(0, 0, 0, 0.22)",  // Elevated product cards
      },
      // Backdrop blur para glass navigation
      backdropBlur: {
        glass: "20px",
      },
      backdropSaturate: {
        glass: "1.8",
      },
      // Transiciones Apple: smooth, 200-300ms
      transitionDuration: {
        DEFAULT: "200ms",
        fast: "150ms",
        slow: "300ms",
      },
      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0.25, 0.1, 0.25, 1)",
        "out-quart": "cubic-bezier(0.25, 1, 0.5, 1)",
        apple: "cubic-bezier(0.42, 0, 0.58, 1)",
      },
      // Spacing Apple (base 8px)
      spacing: {
        0.5: "2px",
        1: "4px",
        1.5: "6px",
        2: "8px",
        2.5: "10px",
        3: "12px",
        3.5: "14px",
        4: "16px",
        5: "20px",
        6: "24px",
        7: "28px",
        8: "32px",
        9: "36px",
        10: "40px",
        11: "44px",  // Touch target mínimo
        12: "48px",
        14: "56px",
        16: "64px",
        20: "80px",
        24: "96px",
      },
      // Max width para contenido centrado (Apple style)
      maxWidth: {
        prose: "980px",  // Apple content width
      },
      // Animaciones
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "pulse-subtle": "pulseSubtle 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSubtle: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
      },
    },
  },
  plugins: [],
};
