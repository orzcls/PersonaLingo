<template>
  <div
    class="group flex gap-4 max-w-4xl mx-auto"
    :class="isUser ? 'flex-row-reverse' : ''"
  >
    <!-- Monogram avatar -->
    <div
      class="shrink-0 w-10 h-10 flex items-center justify-center font-display italic text-[1.2rem] leading-none select-none"
      :class="isUser
        ? 'bg-ochre-500/90 text-paper-50'
        : 'bg-ink-900 text-paper-50'"
      style="border-radius: 2px;"
    >{{ isUser ? 'U' : 'L' }}</div>

    <!-- Message body -->
    <div class="flex-1 min-w-0 max-w-[680px]" :class="isUser ? 'text-right' : ''">
      <div class="flex items-baseline gap-2 mb-1.5"
           :class="isUser ? 'justify-end' : ''">
        <span class="num-chapter">
          {{ isUser ? 'You' : 'Ling, AI coach' }}
        </span>
        <span class="font-mono text-[0.66rem] tabular-nums text-ink-300">
          {{ formatTime(message.timestamp) }}
        </span>
      </div>

      <!-- User line: serif italic, right-aligned quote -->
      <p
        v-if="isUser"
        class="font-serif italic text-ink-900 leading-relaxed whitespace-pre-wrap text-[1.02rem] pl-6 relative"
      >
        <span class="absolute left-0 top-0 font-display text-2xl leading-none text-ochre-500 select-none">&ldquo;</span>
        {{ message.content }}
      </p>

      <!-- Assistant card: paper surface with hairline -->
      <div v-else class="paper-card p-5">
        <p class="font-serif text-ink-700 leading-[1.68] whitespace-pre-wrap">
          {{ message.content }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: Object, required: true }
})

const isUser = computed(() => props.message.role === 'user')

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>
