module.exports = {
  content: [
    "../../templates/**/*.html",
    "../../accounts/templates/**/*.html",
    "../../images/templates/**/*.html",
    "../../actions/templates/**/*.html",
    "../../pages/templates/**/*.html",
    "../../**/templates/**/*.html",
    "../../**/*.py",
    "../templates/**/*.html",
  ],
  darkMode: "class",
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '1.5rem',
        lg: '2rem',
      },
    },
    extend: {
      colors: {
        primary: {
            DEFAULT: "#10B981", // emerald-500
            light: "#34D399", // emerald-400
            dark: "#059669", // emerald-600
        },
        secondary: {
          DEFAULT: "#6366F1", // indigo-500
          light: "#818CF8", // indigo-400
          dark: "#4F46E5", // indigo-600
        },
        // Background colors
        "background-light": "#FFFFFF", // white
        "background-dark": "#111827", // gray-900
        "background-light-alt": "#F9FAFB", // gray-50
        "background-dark-alt": "#1F2937", // gray-800
        // Card colors
        "card-light": "#FFFFFF", // white
        "card-dark": "#334155", // slate-700
        // Text colors
        "text-light-headings": "#111827", // gray-900
        "text-light-body": "#4B5563", // gray-600
        "text-dark-headings": "#F9FAFB", // gray-50
        "text-dark-body": "#D1D5DB", // gray-300
        // Border colors
        "border-light": "#E5E7EB", // gray-200
        "border-dark": "#374151", // gray-700
        // Utility colors
        success: {
          DEFAULT: "#10B981", // emerald-500
          light: "#34D399", // emerald-400
          dark: "#059669", // emerald-600
        },
        error: {
          DEFAULT: "#EF4444", // red-500
          light: "#F87171", // red-400
          dark: "#DC2626", // red-600
        },
        warning: {
          DEFAULT: "#F59E0B", // amber-500
          light: "#FBBF24", // amber-400
          dark: "#D97706", // amber-600
        },
        info: {
          DEFAULT: "#3B82F6", // blue-500
          light: "#60A5FA", // blue-400
          dark: "#2563EB", // blue-600
        },
      },
      fontFamily: {
        display: ["Plus Jakarta Sans", "Playfair Display", "serif"],
        sans: ["Plus Jakarta Sans", "Roboto", "sans-serif"],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        DEFAULT: "0.5rem", // 8px
        'sm': "0.25rem", // 4px
        'md': "0.5rem", // 8px
        'lg': "0.75rem", // 12px
        'xl': "1rem", // 16px
        '2xl': "1.5rem", // 24px
        'full': "9999px",
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
      },
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
};