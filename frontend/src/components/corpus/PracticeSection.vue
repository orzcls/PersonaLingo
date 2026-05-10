<template>
  <section id="practice" class="mb-16 stagger">
    <header class="mb-7">
      <p class="num-chapter text-[11px] mb-2">§ 05 · exercises</p>
      <h2 class="font-display italic text-3xl md:text-4xl text-ink-900 leading-tight">
        Self Practice
      </h2>
      <p class="mt-2 font-serif text-sm text-ink-500 italic max-w-xl">
        Respond before you reveal. The model answer is a courtesy, not a crutch.
      </p>
      <div class="hairline mt-5"></div>
    </header>

    <div class="space-y-6">
      <article
        v-for="(item, i) in practice"
        :key="item.id || i"
        class="paper-card p-6 md:p-7"
      >
        <!-- Question Header -->
        <div class="flex items-start gap-5 mb-5">
          <div class="shrink-0 text-right">
            <p class="num-chapter text-[10px]">no.</p>
            <p class="font-display italic text-3xl text-ochre-500 leading-none mt-0.5">
              {{ String(item.id || i + 1).padStart(2, '0') }}
            </p>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-display italic text-xl text-ink-900 leading-snug">
              {{ item.question }}
            </h3>
            <span
              v-if="item.suggested_anchor"
              class="inline-flex items-center gap-1.5 mt-2 font-mono text-[11px] tracking-widest"
              :class="anchorColor(item.suggested_anchor)"
            >
              ▲ Anchor {{ item.suggested_anchor }}
            </span>
          </div>
        </div>

        <!-- Thinking Guide -->
        <div class="mb-5">
          <p class="field-label mb-3">Thinking Guide</p>
          <ol class="space-y-2.5">
            <li
              v-for="(step, j) in item.thinking_guide"
              :key="j"
              class="flex items-start gap-4"
            >
              <span class="font-mono text-ochre-500 text-[11px] tracking-widest shrink-0 pt-1">
                {{ String(j + 1).padStart(2, '0') }}
              </span>
              <span class="font-serif text-[15px] leading-[1.75] text-ink-700">{{ step }}</span>
            </li>
          </ol>
        </div>

        <!-- Show Model Answer Toggle -->
        <div>
          <button
            @click="toggleAnswer(i)"
            class="inline-flex items-center gap-3 px-4 py-2 border border-ink-900/20 hover:border-ink-900 font-serif italic text-[14px] text-ink-700 hover:text-ink-900 transition-colors"
          >
            <span class="font-mono text-[11px] text-ochre-500 tracking-widest not-italic">
              {{ showAnswers[i] ? '—' : '+' }}
            </span>
            {{ showAnswers[i] ? 'Hide' : 'Reveal' }} Model Answer
          </button>

          <transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-[1200px]"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 max-h-[1200px]"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="showAnswers[i]" class="mt-5 overflow-hidden">
              <!-- Model Answer -->
              <div class="bg-paper-100/50 border-l-2 border-ochre-500 p-5 mb-5">
                <p class="field-label mb-2 text-ochre-500">Model Answer</p>
                <p class="font-serif italic text-[15px] leading-[1.9] text-ink-700 whitespace-pre-line">
                  {{ item.model_answer }}
                </p>
              </div>

              <!-- Self Check -->
              <div v-if="item.self_check && item.self_check.length">
                <p class="field-label mb-3">Self-Check</p>
                <div class="space-y-2">
                  <label
                    v-for="(check, k) in item.self_check"
                    :key="k"
                    class="flex items-start gap-3 cursor-pointer group"
                  >
                    <input
                      type="checkbox"
                      class="mt-1 w-3.5 h-3.5 accent-indigo-600 border-ink-500"
                    />
                    <span class="font-serif text-[14px] leading-relaxed text-ink-700 group-hover:text-ink-900 transition-colors">
                      {{ check }}
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </article>
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

const anchorColor = (id) => {
  const colors = {
    A: 'text-indigo-800',
    B: 'text-ochre-500',
    C: 'text-sage-500',
    D: 'text-rouge-600'
  }
  return colors[id] || 'text-ink-500'
}
</script>
