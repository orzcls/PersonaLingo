<template>
  <div class="hairline-t py-4 px-5 lg:px-8 bg-paper-50/95 backdrop-blur-sm">
    <div class="flex items-end gap-4 max-w-5xl mx-auto">
      <div class="flex-1 relative">
        <label class="field-label block mb-2" for="chat-textarea">Write &mdash; Enter to send, Shift &#x23CE; for a new line</label>
        <textarea
          id="chat-textarea"
          ref="inputRef"
          v-model="inputText"
          @keydown="handleKeydown"
          :disabled="disabled"
          placeholder="Type your note, a question, or a passage of practice&hellip;"
          class="w-full font-serif text-ink-900 bg-transparent resize-none focus:outline-none placeholder:text-ink-300 placeholder:italic disabled:opacity-50 pb-2"
          style="border: none; border-bottom: 1px solid rgba(27,31,42,0.22); padding: .4rem 0; line-height: 1.68;"
          :rows="rows"
        ></textarea>
      </div>

      <button
        @click="send"
        :disabled="disabled || !inputText.trim()"
        class="shrink-0 btn-ink !py-2.5 !px-4 disabled:opacity-40 disabled:cursor-not-allowed"
        aria-label="Send message"
      >
        <span class="font-mono text-[0.66rem] tracking-[0.24em] uppercase">Send</span>
        <svg class="arrow w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M5 12h14m0 0l-6-6m6 6l-6 6" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['send'])

const inputRef = ref(null)
const inputText = ref('')

const rows = computed(() => {
  const lineCount = (inputText.value.match(/\n/g) || []).length + 1
  return Math.min(Math.max(lineCount, 1), 5)
})

function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    send()
  }
}

function send() {
  const text = inputText.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  inputText.value = ''
}
</script>
