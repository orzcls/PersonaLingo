<template>
  <div class="max-w-3xl mx-auto px-4 py-24">
    <!-- 顶部章节标识 -->
    <div class="text-center mb-12">
      <p class="num-chapter mb-6">§ interlude · composing</p>

      <!-- 墨点扩散 Loading 组 -->
      <div class="relative h-28 flex items-center justify-center mb-8">
        <span class="absolute w-24 h-24 rounded-full bg-ochre-500 animate-ink-blot" style="opacity:.08"></span>
        <span class="absolute w-16 h-16 rounded-full bg-ink-900 animate-ink-blot" style="animation-delay:.25s;opacity:.14"></span>
        <span class="relative w-6 h-6 rounded-full bg-ink-900"></span>
      </div>

      <h2 class="font-display italic text-4xl md:text-5xl text-ink-900 mb-3 leading-tight">
        Composing your corpus
      </h2>
      <p class="font-serif italic text-ink-500 text-[15px] max-w-md mx-auto leading-relaxed">
        A private dossier is being hand-set. One line at a time — patience suits the page.
      </p>
    </div>

    <!-- Progress Stages —— 编辑部流程 -->
    <div class="max-w-md mx-auto mb-10">
      <div
        v-for="(hint, idx) in hints"
        :key="idx"
        class="stage-row"
        :class="stageClass(idx)"
      >
        <!-- 左侧状态指示 -->
        <span class="stage-num">
          <template v-if="idx < currentHintIndex">✓</template>
          <template v-else>{{ String(idx + 1).padStart(2, '0') }}</template>
        </span>
        <span class="stage-text font-serif" :class="idx === currentHintIndex ? 'italic text-ink-900' : ''">
          {{ hint }}
        </span>
        <span v-if="idx === currentHintIndex" class="stage-pulse">
          <span class="pulse-dot"></span>
          <span class="pulse-dot" style="animation-delay:.15s"></span>
          <span class="pulse-dot" style="animation-delay:.3s"></span>
        </span>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="max-w-md mx-auto paper-card p-6 border-l-2 border-rouge-600">
      <p class="num-chapter text-[10px] text-rouge-600 mb-2">§ error</p>
      <p class="font-serif italic text-[14px] text-ink-700 mb-4 leading-relaxed">{{ error }}</p>
      <button @click="retryGeneration" class="btn-ink">
        <span>Try again</span>
        <span class="text-ochre-300">↻</span>
      </button>
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
  'Studying your personality profile',
  'Sketching four anchor stories',
  'Drawing bridges between topics',
  'Elevating the vocabulary'
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

function stageClass(idx) {
  if (idx < currentHintIndex.value) return 'is-done'
  if (idx === currentHintIndex.value) return 'is-current'
  return 'is-pending'
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

<style scoped>
.stage-row {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(27, 31, 42, 0.1);
  transition: all .4s cubic-bezier(.2,.8,.2,1);
}
.stage-row.is-pending .stage-num,
.stage-row.is-pending .stage-text {
  color: var(--ink-300, #A7ABB3);
}
.stage-row.is-done .stage-num {
  color: var(--sage-500, #7B8E7A);
}
.stage-row.is-done .stage-text {
  color: var(--ink-500, #5F6572);
  text-decoration: line-through;
  text-decoration-color: rgba(27, 31, 42, 0.2);
}
.stage-row.is-current .stage-num {
  color: var(--ochre-500, #C3822F);
}
.stage-row.is-current .stage-text {
  color: var(--ink-900, #1B1F2A);
}

.stage-num {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-align: right;
}
.stage-text {
  font-size: 15px;
  line-height: 1.6;
}
.stage-pulse {
  display: inline-flex;
  gap: 0.25rem;
}
.pulse-dot {
  width: 4px;
  height: 4px;
  border-radius: 9999px;
  background: var(--ochre-500, #C3822F);
  animation: pulse-bounce 1s cubic-bezier(.4,0,.2,1) infinite;
}
@keyframes pulse-bounce {
  0%, 100% { opacity: .3; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-2px); }
}
</style>
