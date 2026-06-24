import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Theme = 'theme-warm' | 'theme-pro' | 'theme-mini' | 'theme-dark'

export const useThemeStore = defineStore('theme', () => {
  const saved = (localStorage.getItem('theme') as Theme) || 'theme-warm'
  const current = ref<Theme>(saved)

  function setTheme(theme: Theme) {
    current.value = theme
    document.documentElement.classList.remove('theme-warm', 'theme-pro', 'theme-mini', 'theme-dark')
    document.documentElement.classList.add(theme)
    localStorage.setItem('theme', theme)
  }

  const themes = [
    { value: 'theme-warm' as const, label: '温暖陪伴', desc: '暖橙+奶油白' },
    { value: 'theme-pro' as const, label: '专业克制', desc: '深蓝+白' },
    { value: 'theme-mini' as const, label: '现代极简', desc: '极简灰白' },
    { value: 'theme-dark' as const, label: '暗夜沉浸', desc: '深黑+暖橙' },
  ]

  return { current, setTheme, themes }
})
