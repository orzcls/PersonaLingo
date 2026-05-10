<template>
  <article
    class="group relative paper-card pl-8 pr-6 py-5 cursor-pointer transition-all duration-300 hover:translate-x-1"
    @click="$emit('expand', note)"
  >
    <!-- 左侧 ochre/indigo/sage 标记线 -->
    <span class="absolute left-0 top-6 bottom-6 w-[3px]" :class="leftBarColor"></span>

    <div class="flex items-baseline justify-between gap-4 mb-2 flex-wrap">
      <div class="flex items-baseline gap-3 flex-1 min-w-0">
        <span class="num-chapter text-[10px] shrink-0">{{ formatChapter(note.created_at) }}</span>
        <h3 class="font-display italic text-xl text-ink-900 leading-snug truncate group-hover:text-ink-900 transition-colors">
          {{ note.title }}
        </h3>
      </div>
      <span
        class="font-mono text-[10px] tracking-widest shrink-0"
        :class="triggerTypeClass"
      >
        {{ note.trigger_type?.toUpperCase() }}
      </span>
    </div>

    <p class="font-serif text-[14px] leading-[1.75] text-ink-700 mb-4 line-clamp-2 pl-[3.7rem]">
      {{ note.summary }}
    </p>

    <div class="flex items-center justify-between pt-3 border-t border-ink-900/10">
      <span class="font-mono text-[11px] text-ink-500 tracking-wider">{{ formatDate(note.created_at) }}</span>
      <span class="font-serif italic text-[12px] text-ochre-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        read further →
      </span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  note: {
    type: Object,
    required: true
  }
})

defineEmits(['expand'])

const triggerTypeClass = computed(() => {
  const typeMap = {
    'conversation': 'text-ink-500',
    'practice': 'text-ochre-500',
    'review': 'text-sage-500',
    'auto': 'text-ink-500'
  }
  return typeMap[props.note.trigger_type] || typeMap['auto']
})

const leftBarColor = computed(() => {
  const colorMap = {
    'conversation': 'bg-ink-900',
    'practice': 'bg-ochre-500',
    'review': 'bg-sage-500',
    'auto': 'bg-ink-300'
  }
  return colorMap[props.note.trigger_type] || colorMap['auto']
})

function formatChapter(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return `§ ${String(date.getMonth() + 1).padStart(2, '0')}·${String(date.getDate()).padStart(2, '0')}`
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
