<template>
  <div class="scholar-prose max-w-none" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: { type: String, default: '' }
})

const renderedContent = computed(() => {
  if (!props.content) return ''

  let html = props.content

  // Headers
  html = html.replace(/^### (.+)$/gm, '<h3 class="font-display text-[1.25rem] font-semibold text-ink-900 mt-5 mb-2">$1</h3>')
  html = html.replace(/^## (.+)$/gm,  '<h2 class="font-display text-[1.5rem] font-semibold text-ink-900 mt-7 mb-3">$1</h2>')
  html = html.replace(/^# (.+)$/gm,   '<h1 class="font-display text-[1.9rem] font-bold text-ink-900 mt-8 mb-4 tracking-tight">$1</h1>')

  // Bold / italic
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="text-ink-900 font-semibold">$1</strong>')
  html = html.replace(/\*(.+?)\*/g,     '<em class="font-serif italic text-ink-700">$1</em>')

  // Inline code
  html = html.replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 bg-paper-100 hairline rounded-sm font-mono text-[0.85em] text-indigo-800">$1</code>')

  // Lists
  html = html.replace(/^- (.+)$/gm, '<li class="font-serif text-ink-700 ml-4 marker:text-ochre-500">$1</li>')
  html = html.replace(/(<li.*<\/li>\n?)+/g, '<ul class="list-disc space-y-1 my-3 pl-2">$&</ul>')

  // Paragraphs
  html = html.replace(/^(?!<[hulo]|<li)(.+)$/gm, '<p class="font-serif text-ink-700 leading-relaxed mb-3">$1</p>')

  // Blank lines
  html = html.replace(/\n\n/g, '')

  return html
})
</script>

<style scoped>
.scholar-prose :deep(a) {
  color: var(--indigo-800, #1C2A52);
  border-bottom: 1px solid rgba(44, 62, 107, 0.35);
  text-decoration: none;
  transition: border-color .24s;
}
.scholar-prose :deep(a:hover) { border-bottom-color: var(--ochre-500, #B8692B); }

.scholar-prose :deep(blockquote) {
  margin: 1rem 0;
  padding: .4rem 0 .4rem 1rem;
  border-left: 2px solid var(--ochre-500, #B8692B);
  font-family: 'Fraunces', 'Noto Serif SC', Georgia, serif;
  font-style: italic;
  color: var(--ink-700, #2F3342);
}
</style>
