import { defineStore } from 'pinia'

export const useQuestionnaireStore = defineStore('questionnaire', {
  state: () => ({
    currentStep: 1,
    totalSteps: 5,

    // Step 1: MBTI
    mbtiAnswers: {},
    mbtiResult: null,

    // Step 2: Personal Background (新增)
    personalBackground: {
      age: null,
      gender: '',
      zodiac: '',
      profession: '',
      city: '',
      selfDescription: ''
    },

    // Step 3: Interests (增强 - 支持自定义)
    interests: {
      tags: [],        // [{name: 'Photography', isCustom: false}, ...]
      customInput: '',
      descriptions: ['', '', '']
    },

    // Step 4: Life Experiences (新增)
    lifeExperiences: {
      people: [],   // [{relationship, nickname, description, memorableExperience}]
      objects: [],  // [{category, name, significance}]
      places: []    // [{category, name, experience}]
    },

    // Step 5: IELTS Preference
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

    setPersonalBackground(data) {
      this.personalBackground = { ...this.personalBackground, ...data }
    },

    setLifeExperiences(data) {
      this.lifeExperiences = { ...this.lifeExperiences, ...data }
    },

    addPerson(person) {
      this.lifeExperiences.people.push(person)
    },

    removePerson(index) {
      this.lifeExperiences.people.splice(index, 1)
    },

    addObject(obj) {
      this.lifeExperiences.objects.push(obj)
    },

    removeObject(index) {
      this.lifeExperiences.objects.splice(index, 1)
    },

    addPlace(place) {
      this.lifeExperiences.places.push(place)
    },

    removePlace(index) {
      this.lifeExperiences.places.splice(index, 1)
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
      this.personalBackground = { age: null, gender: '', zodiac: '', profession: '', city: '', selfDescription: '' }
      this.interests = { tags: [], customInput: '', descriptions: ['', '', ''] }
      this.lifeExperiences = { people: [], objects: [], places: [] }
      this.ieltsPreference = { targetBand: null, topicTypes: [], examMonth: null }
      this.questionnaireId = null
      this.corpusId = null
    }
  }
})
