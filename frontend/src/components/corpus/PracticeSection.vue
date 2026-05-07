<template>
  <section id="practice" class="mb-12">
    <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
      Self Practice
    </h2>

    <div class="space-y-6">
      <div
        v-for="(item, i) in practice"
        :key="item.id || i"
        class="bg-gray-800 rounded-xl p-6 border border-gray-700/50"
      >
        <!-- Question Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-start gap-3">
            <span class="w-8 h-8 bg-cyan-500/10 border border-cyan-500/30 rounded-lg flex items-center justify-center text-cyan-300 text-sm font-bold flex-shrink-0">
              {{ item.id || i + 1 }}
            </span>
            <h3 class="text-base font-semibold text-white leading-relaxed">{{ item.question }}</h3>
          </div>
          <span
            v-if="item.suggested_anchor"
            class="px-2 py-0.5 rounded text-xs font-bold flex-shrink-0 ml-2"
            :class="anchorBadge(item.suggested_anchor)"
          >
            Anchor {{ item.suggested_anchor }}
          </span>
        </div>

        <!-- Thinking Guide -->
        <div class="mb-4">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Thinking Guide</h4>
          <ol class="space-y-1.5 pl-4">
            <li
              v-for="(step, j) in item.thinking_guide"
              :key="j"
              class="text-gray-400 text-sm list-decimal"
            >
              {{ step }}
            </li>
          </ol>
        </div>

        <!-- Show Model Answer Toggle -->
        <div>
          <button
            @click="toggleAnswer(i)"
            class="flex items-center gap-2 px-4 py-2 bg-gray-700/50 hover:bg-gray-700 border border-gray-600/50 rounded-lg text-sm text-gray-300 hover:text-white transition-all duration-200"
          >
            <svg
              class="w-4 h-4 transition-transform duration-200"
              :class="{ 'rotate-180': showAnswers[i] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            {{ showAnswers[i] ? 'Hide' : 'Show' }} Model Answer
          </button>

          <transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-[1000px]"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 max-h-[1000px]"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="showAnswers[i]" class="mt-4 overflow-hidden">
              <!-- Model Answer -->
              <div class="bg-gray-900/50 rounded-lg p-4 mb-4 border-l-3 border-cyan-500/50">
                <h4 class="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-2">Model Answer</h4>
                <p class="text-gray-300 text-sm leading-relaxed whitespace-pre-line">{{ item.model_answer }}</p>
              </div>

              <!-- Self Check -->
              <div v-if="item.self_check && item.self_check.length">
                <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Self-Check</h4>
                <div class="space-y-2">
                  <label
                    v-for="(check, k) in item.self_check"
                    :key="k"
                    class="flex items-start gap-2.5 cursor-pointer group"
                  >
                    <input
                      type="checkbox"
                      class="mt-0.5 w-4 h-4 rounded border-gray-600 bg-gray-700 text-cyan-500 focus:ring-cyan-500/30 focus:ring-offset-0"
                    />
                    <span class="text-gray-400 text-sm group-hover:text-gray-300 transition-colors">{{ check }}</span>
                  </label>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  practice: {
    type: Array,
    required: true
  }
})

const showAnswers = ref({})

function toggleAnswer(index) {
  showAnswers.value[index] = !showAnswers.value[index]
}

const anchorBadge = (id) => {
  const colors = {
    A: 'bg-cyan-500/20 text-cyan-300',
    B: 'bg-purple-500/20 text-purple-300',
    C: 'bg-amber-500/20 text-amber-300',
    D: 'bg-emerald-500/20 text-emerald-300'
  }
  return colors[id] || 'bg-gray-700 text-gray-300'
}
</script>
