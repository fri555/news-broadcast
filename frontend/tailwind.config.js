/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // 使用 CSS 变量驱动主题
        'app-bg': 'var(--app-bg)',
        'app-card': 'var(--app-card)',
        'app-card2': 'var(--app-card2)',
        'app-text': 'var(--app-text)',
        'app-sub': 'var(--app-sub)',
        'app-muted': 'var(--app-muted)',
        'app-accent': 'var(--app-accent)',
        'app-accent-light': 'var(--app-accent-light)',
        'app-accent-text': 'var(--app-accent-text)',
        'app-border': 'var(--app-border)',
        'app-divider': 'var(--app-divider)',
        // warm 保留用于不受主题影响的地方
        warm: {
          50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa',
          300: '#fdba74', 400: '#fb923c', 500: '#f97316',
          600: '#ea580c', 700: '#c2410c', 800: '#9a3412', 900: '#7c2d12',
        },
      },
      borderRadius: { card: '22px' },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', '"PingFang SC"', '"Hiragino Sans GB"', '"Microsoft YaHei"', '"Helvetica Neue"', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
