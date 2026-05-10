<template>
  <div class="min-h-screen">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <LoadingSpinner />
        <p class="mt-5 font-serif italic text-ink-500 text-sm">{{ t('corpus.loading') }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center max-w-md paper-card p-10">
        <p class="num-chapter text-[11px] mb-3">§ error</p>
        <h2 class="font-display italic text-2xl text-ink-900 mb-3">
          {{ t('corpus.errorTitle') }}
        </h2>
        <p class="font-serif text-sm text-ink-500 italic mb-6 leading-relaxed">{{ error }}</p>
        <button @click="fetchCorpus" class="btn-ink">
          <span>{{ t('corpus.retry') }}</span>
          <span class="text-ochre-300">↻</span>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else-if="corpus" class="pb-28">
      <!-- Page Header -->
      <header class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12">
        <p class="num-chapter mb-3">§ 03 · personal corpus</p>
        <div class="flex items-end justify-between flex-wrap gap-6 mb-2">
          <h1 class="font-display italic text-4xl md:text-5xl text-ink-900 leading-[1.05]">
            {{ t('corpus.title') }}
          </h1>
          <p class="font-serif italic text-ink-500 text-sm max-w-sm">
            {{ t('corpus.subtitle') }}
          </p>
        </div>
        <div class="hairline-strong mt-6"></div>

        <!-- Persona Card -->
        <div class="mt-8">
          <PersonaCard :persona="corpus.persona" />
        </div>
      </header>

      <!-- Sticky Navigation —— 章节式 -->
      <nav class="sticky top-16 z-40 bg-paper-50/92 backdrop-blur-sm border-b border-ink-900/10 mb-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center gap-x-8 overflow-x-auto py-4 scrollbar-hide">
            <button
              v-for="(tab, idx) in tabs"
              :key="tab.id"
              @click="scrollToSection(tab.id)"
              class="corpus-tab whitespace-nowrap"
              :class="activeTab === tab.id ? 'is-active' : ''"
            >
              <span class="font-mono text-[10px] text-ochre-500 tracking-widest mr-2">
                {{ String(idx + 1).padStart(2, '0') }}
              </span>
              <span class="font-serif italic">{{ tab.label }}</span>
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
    <div v-if="corpus" class="fixed bottom-0 left-0 right-0 z-50 bg-paper-50/95 backdrop-blur-sm border-t border-ink-900/15">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
        <router-link to="/chat" class="action-link">
          <span class="font-mono text-[10px] text-ochre-500 tracking-widest">01</span>
          <span>{{ t('corpus.chatBtn') }}</span>
        </router-link>
        <span class="action-divider">·</span>
        <button @click="showUpload = true" class="action-link">
          <span class="font-mono text-[10px] text-ochre-500 tracking-widest">02</span>
          <span>{{ t('corpus.uploadBtn') }}</span>
        </button>
        <span class="action-divider">·</span>
        <button @click="downloadHTML" class="action-link">
          <span class="font-mono text-[10px] text-ochre-500 tracking-widest">03</span>
          <span>Download HTML</span>
        </button>
        <span class="action-divider">·</span>
        <router-link to="/export" class="action-link">
          <span class="font-mono text-[10px] text-ochre-500 tracking-widest">04</span>
          <span>{{ t('corpus.exportSkill') }}</span>
        </router-link>
        <span class="action-divider">·</span>
        <router-link to="/questionnaire" class="action-link">
          <span class="font-mono text-[10px] text-ochre-500 tracking-widest">05</span>
          <span>{{ t('corpus.generateNew') }}</span>
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
import LoadingSpinner from '../components/LoadingSpinner.vue'
import PersonaCard from '../components/corpus/PersonaCard.vue'
import AnchorSection from '../components/corpus/AnchorSection.vue'
import BridgeSection from '../components/corpus/BridgeSection.vue'
import VocabularySection from '../components/corpus/VocabularySection.vue'
import PatternSection from '../components/corpus/PatternSection.vue'
import PracticeSection from '../components/corpus/PracticeSection.vue'
import { useI18n } from '../i18n'

const { t } = useI18n()

const router = useRouter()
const store = useQuestionnaireStore()

const loading = ref(true)
const error = ref(null)
const corpus = ref(null)
const activeTab = ref('anchors')
const showUpload = ref(false)

const tabs = [
  { id: 'anchors', label: 'Anchors' },
  { id: 'bridges', label: 'Bridges' },
  { id: 'vocabulary', label: 'Vocabulary' },
  { id: 'patterns', label: 'Patterns' },
  { id: 'practice', label: 'Practice' }
]

function scrollToSection(id) {
  activeTab.value = id
  const el = document.getElementById(id)
  if (el) {
    const offset = 140
    const top = el.getBoundingClientRect().top + window.scrollY - offset
    window.scrollTo({ top, behavior: 'smooth' })
  }
}

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
  setTimeout(() => {
    setupObserver()
  }, 100)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.corpus-tab {
  position: relative;
  padding: 0.25rem 0;
  color: var(--ink-500, #5F6572);
  transition: color .2s ease;
}
.corpus-tab:hover { color: var(--ink-900, #1B1F2A); }
.corpus-tab::after {
  content: '';
  position: absolute;
  left: 0; right: 100%;
  bottom: -2px;
  height: 2px;
  background: var(--ochre-500, #C3822F);
  transition: right .25s cubic-bezier(.2,.8,.2,1);
}
.corpus-tab.is-active { color: var(--ink-900, #1B1F2A); }
.corpus-tab.is-active::after { right: 30%; }

.action-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 13px;
  color: var(--ink-700, #2B303C);
  transition: color .2s ease;
}
.action-link:hover { color: var(--ink-900, #1B1F2A); }
.action-divider { color: var(--ink-300, #A7ABB3); font-family: 'Fraunces', serif; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
