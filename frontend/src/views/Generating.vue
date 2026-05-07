<template>
  <div class="max-w-4xl mx-auto px-4 py-20">
    <div class="text-center">
      <!-- Animated Icon -->
      <div class="relative w-24 h-24 mx-auto mb-8">
        <div class="absolute inset-0 bg-accent-500/20 rounded-full animate-ping" />
        <div class="relative w-24 h-24 bg-dark-800 border border-accent-400/30 rounded-full flex items-center justify-center">
          <svg class="w-10 h-10 text-accent-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
      </div>

      <!-- Title -->
      <h2 class="text-2xl font-bold text-white mb-3">Generating Your Corpus</h2>
      <p class="text-dark-400 mb-10">This may take a moment. We're building something unique for you.</p>

      <!-- Progress Stages -->
      <div class="max-w-md mx-auto space-y-3 mb-10">
        <div
          v-for="(hint, idx) in hints"
          :key="idx"
          :class="[
            'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-500',
            idx < currentHintIndex
              ? 'bg-dark-800/50 border border-accent-400/20'
              : idx === currentHintIndex
                ? 'bg-dark-800 border border-accent-400/40 shadow-lg shadow-accent-500/5'
                : 'bg-dark-800/30 border border-dark-700'
          ]"
        >
          <span v-if="idx < currentHintIndex" class="text-accent-400 text-sm">✓</span>
          <span v-else-if="idx === currentHintIndex" class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-400 opacity-75" />
            <span class="relative inline-flex rounded-full h-3 w-3 bg-accent-400" />
          </span>
          <span v-else class="w-3 h-3 rounded-full bg-dark-600" />
          <span :class="[
            'text-sm',
            idx < currentHintIndex ? 'text-accent-300' : idx === currentHintIndex ? 'text-white font-medium' : 'text-dark-500'
          ]">
            {{ hint }}
          </span>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="max-w-md mx-auto bg-red-500/10 border border-red-500/30 rounded-xl p-4 mt-6">
        <p class="text-red-400 text-sm mb-3">{{ error }}</p>
        <button
          class="px-4 py-2 bg-red-500/20 text-red-300 rounded-lg text-sm hover:bg-red-500/30 transition-all"
          @click="retryGeneration"
        >
          Retry
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuestionnaireStore } from '../stores/questionnaire'
import { generateCorpus } from '../api/index.js'

const router = useRouter()
const store = useQuestionnaireStore()

const hints = [
  'Analyzing your personality profile...',
  'Generating personalized anchors...',
  'Creating topic bridges...',
  'Building vocabulary upgrades...',
]

const currentHintIndex = ref(0)
const error = ref('')
let timer = null

function startHintAnimation() {
  timer = setInterval(() => {
    if (currentHintIndex.value < hints.length - 1) {
      currentHintIndex.value++
    }
  }, 3000)
}

async function startGeneration() {
  error.value = ''
  currentHintIndex.value = 0
  startHintAnimation()

  try {
    const questionnaireId = store.questionnaireId
    if (!questionnaireId) {
      throw new Error('No questionnaire ID found. Please complete the questionnaire first.')
    }

    const response = await generateCorpus(questionnaireId)
    store.setCorpusId(response.id || response.corpus_id)

    // Show completion briefly
    currentHintIndex.value = hints.length
    if (timer) clearInterval(timer)

    setTimeout(() => {
      router.push('/corpus')
    }, 800)
  } catch (err) {
    if (timer) clearInterval(timer)
    console.error('Generation error:', err)
    error.value = err?.response?.data?.message || err.message || 'Failed to generate corpus. Please try again.'
  }
}

function retryGeneration() {
  startGeneration()
}

onMounted(() => {
  startGeneration()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
