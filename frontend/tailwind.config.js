/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Nunito"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Fraunces"', 'Georgia', 'ui-serif', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        // Warm paper background and readable ink
        cream: {
          50: '#fffdf8', 100: '#fff8ea', 200: '#fdeed4', 300: '#f9dfb4',
        },
        // 50-300 are the light end, kept so the detailed reference view keeps
        // resolving; 400-900 are the readable ink used by the new surfaces.
        ink: {
          50: '#fdfcf9', 100: '#f4f2ec', 200: '#e6e3d9', 300: '#cbc7b9',
          400: '#8a8578', 500: '#6b6659', 600: '#544f44',
          700: '#413d34', 800: '#302d27', 900: '#211f1b',
        },
        accent: {
          50: '#fff8ea', 100: '#fdeed4', 200: '#f9dfb4', 300: '#fbbf24',
          400: '#fbbf24', 500: '#f59e0b', 600: '#d97706', 700: '#b45309',
        },
        // The three finding groups
        good: {
          50: '#effdf4', 100: '#d8fbe5', 200: '#b2f5cd', 300: '#79e9ac',
          400: '#3fd486', 500: '#1cb968', 600: '#119553', 700: '#117645',
          800: '#135d39', 900: '#124c31',
        },
        hard: {
          50: '#fff1f2', 100: '#ffe0e3', 200: '#ffc6cc', 300: '#ff9aa6',
          400: '#fb6076', 500: '#f2334c', 600: '#df1734', 700: '#bb0f28',
          800: '#9c1026', 900: '#851226',
        },
        calm: {
          50: '#f5f7ff', 100: '#e9edff', 200: '#d5ddff', 300: '#b4c2ff',
          400: '#8b9cfc', 500: '#6975f5', 600: '#4d51e9', 700: '#4041ce',
          800: '#3639a6', 900: '#333783',
        },
        sun: { 400: '#fbbf24', 500: '#f59e0b', 600: '#d97706' },
      },
      boxShadow: {
        card: '0 1px 2px rgba(33,31,27,.04), 0 8px 24px -12px rgba(33,31,27,.18)',
        lift: '0 2px 4px rgba(33,31,27,.05), 0 18px 40px -18px rgba(33,31,27,.28)',
      },
      borderRadius: { xl2: '1.25rem' },
      keyframes: {
        pop: { '0%': { opacity: 0, transform: 'translateY(6px)' },
               '100%': { opacity: 1, transform: 'translateY(0)' } },
      },
      animation: { pop: 'pop .28s ease-out both' },
    },
  },
  plugins: [],
}
