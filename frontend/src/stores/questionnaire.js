import { defineStore } from 'pinia'

export const useQuestionnaireStore = defineStore('questionnaire', {
  state: () => ({
    currentStep: 1,
    totalSteps: 3,
    // MBTI: stores answer for each of the 12 questions { questionId: 'a' | 'b' }
    mbtiAnswers: {},
    // Computed MBTI type string e.g. 'INFP'
    mbtiResult: null,
    // Interest data
    interests: {
      tags: [],
      descriptions: ['', '', '']
    },
    // IELTS preferences
    ieltsPreference: {
      targetBand: null,
      topicTypes: [],
      examMonth: null
    },
    // IDs
    questionnaireId: null,
    corpusId: null
  }),

  getters: {
    isFirstStep: (state) => state.currentStep === 1,
    isLastStep: (state) => state.currentStep === state.totalSteps,
    progress: (state) => (state.currentStep / state.totalSteps) * 100
  },

  actions: {
    nextStep() {
      if (this.currentStep < this.totalSteps) {
        this.currentStep++
      }
    },

    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--
      }
    },

    setMBTIAnswer(questionId, answer) {
      this.mbtiAnswers[questionId] = answer
    },

    setMBTIResult(result) {
      this.mbtiResult = result
    },

    setInterestTags(tags) {
      this.interests.tags = tags
    },

    setInterestDescription(index, text) {
      this.interests.descriptions[index] = text
    },

    setIELTSPreference(preference) {
      this.ieltsPreference = { ...this.ieltsPreference, ...preference }
    },

    setQuestionnaireId(id) {
      this.questionnaireId = id
    },

    setCorpusId(id) {
      this.corpusId = id
    },

    reset() {
      this.currentStep = 1
      this.mbtiAnswers = {}
      this.mbtiResult = null
      this.interests = { tags: [], descriptions: ['', '', ''] }
      this.ieltsPreference = { targetBand: null, topicTypes: [], examMonth: null }
      this.questionnaireId = null
      this.corpusId = null
    }
  }
})
