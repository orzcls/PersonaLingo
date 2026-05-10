import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCorpusStore = defineStore('corpus', () => {
  const currentCorpusId = ref(localStorage.getItem('corpusId') || '')
  const corpusData = ref(null)

  function setCorpusId(id) {
    currentCorpusId.value = id
    localStorage.setItem('corpusId', id)
  }

  function setCorpusData(data) {
    corpusData.value = data
  }

  function clear() {
    currentCorpusId.value = ''
    corpusData.value = null
    localStorage.removeItem('corpusId')
  }

  return { currentCorpusId, corpusData, setCorpusId, setCorpusData, clear }
})
