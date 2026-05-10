import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const settings = ref({
    llmProvider: 'openai',
    targetScore: '6.5',
    apiKeyConfigured: false
  })

  function updateSettings(newSettings) {
    settings.value = { ...settings.value, ...newSettings }
  }

  return { settings, updateSettings }
})
