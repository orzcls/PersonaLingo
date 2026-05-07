<template>
  <div class="min-h-screen bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <div class="w-12 h-12 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-400 text-sm">Loading your corpus...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center max-w-md">
        <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-white mb-2">Failed to load corpus</h2>
        <p class="text-gray-400 text-sm mb-4">{{ error }}</p>
        <button @click="fetchCorpus" class="px-4 py-2 bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 rounded-lg text-sm hover:bg-cyan-500/30 transition-colors">
          Retry
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="corpus" class="pb-24">
      <!-- Page Header -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-white mb-2">Your Personalized Corpus</h1>
          <p class="text-gray-400">AI-generated IELTS Speaking materials tailored to your personality and interests</p>
        </div>

        <!-- Persona Card -->
        <PersonaCard :persona="corpus.persona" />
      </div>

      <!-- Sticky Navigation -->
      <nav class="sticky top-16 z-40 bg-gray-900/95 backdrop-blur-sm border-b border-gray-800 mb-8">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center gap-1 overflow-x-auto py-3 scrollbar-hide">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="scrollToSection(tab.id)"
              class="px-4 py-2 text-sm font-medium whitespace-nowrap rounded-lg transition-all duration-200"
              :class="activeTab === tab.id
                ? 'text-cyan-300 bg-cyan-500/10 border-b-2 border-cyan-400'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
      </nav>

      <!-- Sections -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <AnchorSection :anchors="corpus.anchors || []" />
        <BridgeSection :bridges="corpus.bridges || []" />
        <VocabularySection :vocabulary="corpus.vocabulary || []" />
        <PatternSection :patterns="corpus.patterns || []" />
        <PracticeSection :practice="corpus.practice || []" />
      </div>
    </div>

    <!-- Bottom Action Bar -->
    <div v-if="corpus" class="fixed bottom-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-sm border-t border-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-center gap-3">
        <button
          @click="downloadHTML"
          class="px-4 py-2 bg-gray-700/50 hover:bg-gray-700 border border-gray-600/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download HTML
        </button>
        <router-link
          to="/export"
          class="px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 rounded-lg text-sm text-cyan-300 hover:text-cyan-200 transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Export as Skill
        </router-link>
        <router-link
          to="/questionnaire"
          class="px-4 py-2 bg-gray-700/50 hover:bg-gray-700 border border-gray-600/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Generate New
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuestionnaireStore } from '../stores/questionnaire'
import { getCorpus } from '../api/index'
import PersonaCard from '../components/corpus/PersonaCard.vue'
import AnchorSection from '../components/corpus/AnchorSection.vue'
import BridgeSection from '../components/corpus/BridgeSection.vue'
import VocabularySection from '../components/corpus/VocabularySection.vue'
import PatternSection from '../components/corpus/PatternSection.vue'
import PracticeSection from '../components/corpus/PracticeSection.vue'

const router = useRouter()
const store = useQuestionnaireStore()

const loading = ref(true)
const error = ref(null)
const corpus = ref(null)
const activeTab = ref('anchors')

const tabs = [
  { id: 'anchors', label: 'Anchors' },
  { id: 'bridges', label: 'Bridges' },
  { id: 'vocabulary', label: 'Vocabulary' },
  { id: 'patterns', label: 'Patterns' },
  { id: 'practice', label: 'Practice' }
]

// Scroll to section
function scrollToSection(id) {
  activeTab.value = id
  const el = document.getElementById(id)
  if (el) {
    const offset = 140 // sticky nav height
    const top = el.getBoundingClientRect().top + window.scrollY - offset
    window.scrollTo({ top, behavior: 'smooth' })
  }
}

// Intersection observer for active tab tracking
let observer = null

function setupObserver() {
  const options = {
    rootMargin: '-150px 0px -60% 0px',
    threshold: 0
  }
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        activeTab.value = entry.target.id
      }
    })
  }, options)

  tabs.forEach(tab => {
    const el = document.getElementById(tab.id)
    if (el) observer.observe(el)
  })
}

// Fetch corpus data
async function fetchCorpus() {
  loading.value = true
  error.value = null

  const corpusId = store.corpusId
  if (!corpusId) {
    router.push('/')
    return
  }

  try {
    const data = await getCorpus(corpusId)
    corpus.value = data.corpus
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'An error occurred'
  } finally {
    loading.value = false
  }
}

// Download as HTML
function downloadHTML() {
  const htmlContent = document.documentElement.outerHTML
  const blob = new Blob([htmlContent], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `corpus_${store.corpusId || 'export'}.html`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  await fetchCorpus()
  // Setup intersection observer after data loads
  setTimeout(() => {
    setupObserver()
  }, 100)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>
