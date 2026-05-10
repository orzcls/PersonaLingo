<template>
  <article
    class="group paper-card p-5 cursor-pointer transition-all duration-300 hover:translate-y-[-2px]"
    :class="{ 'ring-1 ring-ochre-500/60': expanded }"
    @click="$emit('toggle')"
  >
    <!-- Header -->
    <div class="flex items-start justify-between gap-3 mb-3">
      <div class="flex items-baseline gap-2 flex-wrap flex-1 min-w-0">
        <span class="font-mono text-[10px] tracking-widest" :class="partColor">
          {{ topic.part }}
        </span>
        <span class="font-mono text-[10px] text-ink-500 tracking-wider">/ {{ topic.category }}</span>
        <span
          v-if="topic.linked_p2_id"
          class="font-mono text-[10px] text-sage-500 tracking-widest"
        >
          · P2↗
        </span>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <span
          v-if="topic.is_new"
          class="font-mono text-[10px] text-rouge-600 tracking-widest animate-pulse"
        >
          ◦ NEW
        </span>
        <span
          class="font-mono text-[11px] text-ink-500 transition-transform duration-300"
          :class="{ 'rotate-180': expanded }"
        >⌄</span>
      </div>
    </div>

    <!-- Title -->
    <h3 class="font-display italic text-xl text-ink-900 leading-snug mb-4 group-hover:text-ink-900 transition-colors">
      {{ topic.title }}
    </h3>

    <!-- Questions Preview (collapsed) -->
    <ul v-if="!expanded" class="space-y-2 mb-4">
      <li
        v-for="(q, idx) in topic.questions?.slice(0, 2)"
        :key="idx"
        class="flex items-start gap-3"
      >
        <span class="font-mono text-ochre-500 text-[10px] tracking-widest shrink-0 pt-1">
          {{ String(idx + 1).padStart(2, '0') }}
        </span>
        <span class="font-serif text-[14px] leading-relaxed text-ink-700">{{ q }}</span>
      </li>
      <li v-if="topic.questions?.length > 2" class="font-serif italic text-[12px] text-ink-500 pl-8">
        · {{ topic.questions.length - 2 }} more
      </li>
    </ul>

    <!-- Expanded Details -->
    <div v-if="expanded" class="space-y-5 mb-4">
      <!-- Full Questions List -->
      <div>
        <p class="field-label mb-3">Questions</p>
        <ol class="space-y-2.5">
          <li
            v-for="(q, idx) in topic.questions"
            :key="idx"
            class="flex items-start gap-3"
          >
            <span class="font-mono text-ochre-500 text-[10px] tracking-widest shrink-0 pt-1">
              {{ String(idx + 1).padStart(2, '0') }}
            </span>
            <span class="font-serif text-[14px] leading-[1.75] text-ink-700">{{ q }}</span>
          </li>
        </ol>
      </div>

      <!-- Recommended Anchors -->
      <div v-if="topic.recommended_anchors?.length">
        <p class="field-label mb-2">Recommended Anchors</p>
        <div class="flex flex-wrap gap-x-4 gap-y-1">
          <span
            v-for="anchor in topic.recommended_anchors"
            :key="anchor"
            class="font-mono text-[11px] text-ochre-500 tracking-widest"
          >
            ▲ {{ anchor }}
          </span>
        </div>
      </div>

      <!-- Start Practice -->
      <div class="pt-2">
        <button
          @click.stop
          class="inline-flex items-center gap-2 px-4 py-2 bg-ink-900 text-paper-50 font-serif italic text-[13px] hover:bg-ink-700 transition-colors"
        >
          Begin Practice
          <span class="text-ochre-300">→</span>
        </button>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex items-center justify-between pt-3 border-t border-ink-900/10">
      <div class="flex items-center gap-2">
        <span class="font-mono text-[10px] text-ink-500 tracking-widest">DIFF</span>
        <div class="flex gap-1">
          <span
            v-for="i in 3"
            :key="i"
            class="w-2 h-2 rounded-full border border-ochre-500 transition-colors"
            :class="i <= difficultyLevel ? 'bg-ochre-500' : 'bg-transparent'"
          ></span>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a
          v-if="topic.source_url"
          :href="topic.source_url"
          target="_blank"
          rel="noopener noreferrer"
          @click.stop
          class="font-mono text-[10px] text-indigo-800 tracking-wider hover:underline"
          :title="topic.source_url"
        >↗ source</a>
        <span v-if="topic.season" class="font-mono text-[10px] text-ink-500 tracking-wider">
          {{ topic.season }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  topic: {
    type: Object,
    required: true
  },
  expanded: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])

const partColor = computed(() => {
  switch (props.topic.part) {
    case 'P1': return 'text-indigo-800'
    case 'P2': return 'text-ochre-500'
    case 'P3': return 'text-rouge-600'
    default: return 'text-ink-500'
  }
})

const difficultyLevel = computed(() => {
  switch (props.topic.difficulty) {
    case 'easy': return 1
    case 'medium': return 2
    case 'hard': return 3
    default: return 2
  }
})
</script>
