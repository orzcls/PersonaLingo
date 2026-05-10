<template>
  <div class="flex h-[calc(100vh-4.5rem-3rem)] bg-paper-50">
    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Chat Header -->
      <div class="hairline-b px-5 lg:px-10 py-5 flex items-end justify-between gap-4">
        <div>
          <p class="num-chapter">&sect; 05 &middot; Chat maintenance</p>
          <h1 class="font-display text-[1.7rem] text-ink-900 leading-tight mt-1 tracking-tight"
              style="font-variation-settings: 'opsz' 72, 'SOFT' 40;">
            {{ t('chat.title') }}
          </h1>
          <p class="mt-1 font-serif italic text-ink-500 text-sm">
            {{ t('chat.corpusId') }}:
            <span class="not-italic font-mono text-ochre-500">{{ corpusId || t('chat.notLinked') }}</span>
          </p>
        </div>

        <button
          @click="showExtractor = !showExtractor"
          class="btn-ghost"
          :class="{ 'chip-ink-selected-slim border-ink-900': showExtractor }"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span class="font-mono text-[0.66rem] tracking-[0.22em] uppercase">
            {{ t('chat.extractor') }}
          </span>
        </button>
      </div>

      <!-- Messages Area -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto px-5 lg:px-10 py-8 space-y-8">
        <!-- Welcome state -->
        <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center max-w-md">
            <div class="mx-auto mb-6 w-20 h-20 relative">
              <span class="absolute inset-0 rounded-full bg-indigo-800/90 animate-ink-blot" style="animation-delay: 0ms;"></span>
              <span class="absolute inset-2 rounded-full bg-indigo-800/60 animate-ink-blot" style="animation-delay: 200ms;"></span>
              <span class="absolute inset-[14px] rounded-full bg-ochre-500/80 animate-ink-blot" style="animation-delay: 400ms;"></span>
            </div>
            <p class="num-chapter mb-2">A new conversation</p>
            <h2 class="font-display text-2xl text-ink-900 mb-3 tracking-tight"
                style="font-variation-settings: 'opsz' 72, 'SOFT' 40;">
              {{ t('chat.emptyState') }}
            </h2>
            <p class="font-serif italic text-ink-500 leading-relaxed">
              {{ t('chat.emptyHint') }}
            </p>
          </div>
        </div>

        <!-- Message list -->
        <ChatMessage
          v-for="(msg, idx) in messages"
          :key="idx"
          :message="msg"
        />

        <!-- Loading indicator -->
        <div v-if="loading" class="max-w-4xl mx-auto flex gap-4">
          <div class="shrink-0 w-10 h-10 flex items-center justify-center bg-indigo-800 text-paper-50 font-display italic text-[1.2rem] leading-none select-none" style="border-radius: 2px;">L</div>
          <div class="paper-card px-5 py-4 inline-flex items-center gap-3 min-w-[120px]">
            <span v-for="d in 3" :key="d"
                  class="inline-block w-1.5 h-1.5 rounded-full bg-indigo-800 animate-ink-blot"
                  :style="{ animationDelay: (d * 150) + 'ms' }"></span>
            <span class="font-serif italic text-ink-500 text-sm">Ling is thinking&hellip;</span>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <ChatInput @send="sendMessage" :disabled="loading" />
    </div>

    <!-- Right Sidebar: Corpus Extractor -->
    <aside
      v-if="showExtractor"
      class="w-96 hairline-l px-6 py-6 bg-paper-100/40 overflow-y-auto shrink-0"
    >
      <CorpusExtractor :items="extractedItems" @merge="mergeItems" />
    </aside>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import ChatMessage from '../components/chat/ChatMessage.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import CorpusExtractor from '../components/chat/CorpusExtractor.vue'
import { useI18n } from '../i18n'

const { t } = useI18n()

const corpusId = ref('mock-corpus-001')
const messages = ref([])
const loading = ref(false)
const showExtractor = ref(true)
const messagesContainer = ref(null)

// Mock extracted items
const extractedItems = ref({
  anchors: [
    'I grew up in a small city in Sichuan province',
    'My passion for technology started in high school'
  ],
  vocabulary: [
    'cutting-edge technology',
    'interpersonal skills',
    'thought-provoking'
  ],
  bridges: [
    'Speaking of which...',
    'That reminds me of...'
  ],
  patterns: [
    'I would say that... because...',
    'From my perspective...'
  ]
})

async function sendMessage(text) {
  messages.value.push({
    role: 'user',
    content: text,
    timestamp: new Date().toISOString()
  })

  await scrollToBottom()
  loading.value = true

  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: getMockResponse(text),
      timestamp: new Date().toISOString()
    })
    loading.value = false
    scrollToBottom()
  }, 1500)
}

function getMockResponse(userText) {
  const responses = [
    "That's a great point! I can help you develop a more natural response for this topic. Let me suggest some vocabulary and sentence patterns you could use.",
    "Based on your personality profile, here's how you might naturally answer this question. I've identified some anchors and bridges that align with your speaking style.",
    "I've extracted some useful phrases from our conversation. You can review them in the Corpus Extractor panel and merge the ones you'd like to keep into your corpus.",
    "Let me help you practice this topic. Try incorporating these transition phrases to make your answer more coherent and natural-sounding."
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

function mergeItems(merged) {
  console.log('Merging items:', merged)
  messages.value.push({
    role: 'assistant',
    content: `Successfully merged ${Object.values(merged).flat().length} items into your corpus!`,
    timestamp: new Date().toISOString()
  })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>
