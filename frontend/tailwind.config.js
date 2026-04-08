/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Geist",
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "sans-serif",
        ],
        mono: [
          "Geist Mono",
          '"SF Mono"',
          "Monaco",
          '"Cascadia Code"',
          '"Courier New"',
          "monospace",
        ],
      },
      colors: {
        // Neutrales tintados azul-grisáceo industrial (OKLCH)
        neutral: {
          50: "oklch(98% 0.003 250)",   // bg-page, casi blanco tintado
          100: "oklch(96% 0.005 250)",  // bg-card, superficie elevada
          200: "oklch(92% 0.008 250)",  // border-subtle
          300: "oklch(85% 0.012 250)",  // border-default
          400: "oklch(70% 0.015 250)",  // text-muted, placeholders
          500: "oklch(55% 0.018 250)",  // text-secondary
          600: "oklch(40% 0.020 250)",  // text-primary
          700: "oklch(30% 0.022 250)",  // headings, emphasis
          800: "oklch(22% 0.020 250)",  // casi negro, títulos grandes
          900: "oklch(15% 0.015 250)",  // máximo contraste
        },
        // Primario: azul petróleo industrial sobrio
        primary: {
          50: "oklch(96% 0.020 250)",
          100: "oklch(92% 0.035 250)",
          200: "oklch(85% 0.050 250)",
          300: "oklch(75% 0.070 250)",
          400: "oklch(65% 0.090 250)",
          500: "oklch(55% 0.110 250)",  // azul petróleo base
          600: "oklch(48% 0.120 250)",  // hover, activo
          700: "oklch(40% 0.110 250)",  // pressed
          800: "oklch(32% 0.095 250)",
          900: "oklch(25% 0.075 250)",
        },
        // Semánticos profesionales (alta saturación, legibles)
        success: {
          50: "oklch(96% 0.030 145)",
          100: "oklch(90% 0.060 145)",
          200: "oklch(82% 0.090 145)",
          300: "oklch(72% 0.120 145)",
          400: "oklch(62% 0.145 145)",
          500: "oklch(52% 0.165 145)",  // verde industrial
          600: "oklch(45% 0.160 145)",  // operativo, success
          700: "oklch(38% 0.145 145)",
          800: "oklch(30% 0.120 145)",
          900: "oklch(24% 0.095 145)",
        },
        warning: {
          50: "oklch(96% 0.025 85)",
          100: "oklch(92% 0.055 85)",
          200: "oklch(85% 0.095 85)",
          300: "oklch(78% 0.130 85)",
          400: "oklch(70% 0.155 85)",
          500: "oklch(62% 0.175 85)",   // amarillo-naranja profesional
          600: "oklch(55% 0.170 85)",   // advertencia
          700: "oklch(48% 0.155 85)",
          800: "oklch(40% 0.130 85)",
          900: "oklch(32% 0.105 85)",
        },
        danger: {
          50: "oklch(96% 0.022 25)",
          100: "oklch(92% 0.048 25)",
          200: "oklch(86% 0.085 25)",
          300: "oklch(78% 0.125 25)",
          400: "oklch(68% 0.160 25)",
          500: "oklch(58% 0.185 25)",   // rojo industrial
          600: "oklch(50% 0.195 25)",   // crítico, error
          700: "oklch(42% 0.180 25)",
          800: "oklch(34% 0.150 25)",
          900: "oklch(27% 0.120 25)",
        },
        info: {
          50: "oklch(96% 0.018 240)",
          100: "oklch(92% 0.032 240)",
          200: "oklch(86% 0.050 240)",
          300: "oklch(78% 0.075 240)",
          400: "oklch(68% 0.095 240)",
          500: "oklch(58% 0.110 240)",
          600: "oklch(50% 0.118 240)",
          700: "oklch(42% 0.105 240)",
          800: "oklch(34% 0.085 240)",
          900: "oklch(27% 0.070 240)",
        },
      },
      borderRadius: {
        sm: "6px",   // chips, badges, nav items
        DEFAULT: "8px",   // botones, inputs
        md: "10px",  // cards pequeñas
        lg: "12px",  // cards principales, modales
      },
      fontSize: {
        // Escala fija (4 niveles visuales) para UI densa de operación.
        xs: ["0.75rem", { lineHeight: "1rem", letterSpacing: "0" }],
        sm: ["0.875rem", { lineHeight: "1.375rem", letterSpacing: "0" }],
        base: ["0.875rem", { lineHeight: "1.375rem", letterSpacing: "0" }],
        lg: ["1.125rem", { lineHeight: "1.625rem", letterSpacing: "-0.01em" }],
        xl: ["1.875rem", { lineHeight: "2.25rem", letterSpacing: "-0.02em" }],
      },
      fontWeight: {
        normal: "400",
        medium: "500",
        semibold: "600",
      },
      lineHeight: {
        tight: "1.2",
        normal: "1.5",
        relaxed: "1.7",
      },
      letterSpacing: {
        tighter: "-0.02em",
        tight: "-0.01em",
        normal: "0",
      },
      boxShadow: {
        sm: "0 1px 2px 0 oklch(15% 0.015 250 / 0.05)",
        DEFAULT: "0 1px 3px 0 oklch(15% 0.015 250 / 0.1), 0 1px 2px -1px oklch(15% 0.015 250 / 0.1)",
        md: "0 4px 6px -1px oklch(15% 0.015 250 / 0.1), 0 2px 4px -2px oklch(15% 0.015 250 / 0.1)",
      },
      transitionTimingFunction: {
        "out-quart": "cubic-bezier(0.25, 1, 0.5, 1)",
      },
    },
  },
  plugins: [],
};
