<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
    <!-- Page Header -->
    <header class="text-center mb-16 space-y-3">
      <p class="num-chapter">§ 09 · Atelier exports</p>
      <h1 class="font-display text-5xl sm:text-6xl text-ink-900"
          style="font-variation-settings:'opsz' 144, 'SOFT' 50;">
        {{ t('export.title') }}
      </h1>
      <p class="text-ink-500 font-serif italic max-w-2xl mx-auto">{{ t('export.subtitle') }}</p>
    </header>

    <!-- ─── Corpus Download Section ─── -->
    <section class="mb-16">
      <h2 class="rule-heading font-display italic text-ink-900 text-xl mb-8">
        <span class="px-4">{{ t('export.downloadCorpus') }}</span>
      </h2>

      <div class="grid md:grid-cols-2 gap-5">
        <!-- HTML Download -->
        <article class="paper-card p-7 transition-colors duration-300 hover:bg-paper-100/50">
          <div class="flex items-start gap-5">
            <div class="w-12 h-12 hairline flex items-center justify-center shrink-0 bg-paper-50">
              <svg class="w-5 h-5 text-ink-900" fill="none" stroke="currentColor" stroke-width="1.25" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-mono text-[10px] tracking-[0.22em] text-ochre-500 mb-1">01 · HTML</p>
              <h3 class="font-display italic text-ink-900 text-lg mb-2">{{ t('export.htmlFile') }}</h3>
              <p class="text-ink-500 text-sm font-serif italic mb-5 leading-relaxed">{{ t('export.htmlDesc') }}</p>
              <button @click="downloadCorpus('html')" class="btn-ink text-sm">
                <span class="flex items-center gap-2">{{ t('export.downloadHtml') }} <span class="text-ochre-300">↓</span></span>
              </button>
            </div>
          </div>
        </article>

        <!-- JSON Download -->
        <article class="paper-card p-7 transition-colors duration-300 hover:bg-paper-100/50">
          <div class="flex items-start gap-5">
            <div class="w-12 h-12 hairline flex items-center justify-center shrink-0 bg-paper-50">
              <svg class="w-5 h-5 text-ink-900" fill="none" stroke="currentColor" stroke-width="1.25" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-mono text-[10px] tracking-[0.22em] text-ochre-500 mb-1">02 · JSON</p>
              <h3 class="font-display italic text-ink-900 text-lg mb-2">{{ t('export.jsonData') }}</h3>
              <p class="text-ink-500 text-sm font-serif italic mb-5 leading-relaxed">{{ t('export.jsonDesc') }}</p>
              <button @click="downloadCorpus('json')" class="btn-ink text-sm">
                <span class="flex items-center gap-2">{{ t('export.downloadJson') }} <span class="text-ochre-300">↓</span></span>
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>

    <!-- ─── Skill Export Section ─── -->
    <section class="mb-16">
      <h2 class="rule-heading font-display italic text-ink-900 text-xl mb-3">
        <span class="px-4">{{ t('export.skillExport') }}</span>
      </h2>
      <p class="text-ink-500 text-sm font-serif italic text-center mb-8 max-w-2xl mx-auto">
        {{ t('export.skillExportDesc') }}
      </p>

      <div class="grid md:grid-cols-2 gap-5">
        <article v-for="(fmt, idx) in skillFormats" :key="fmt.id"
                 class="paper-card p-7 flex flex-col transition-colors duration-300 hover:bg-paper-100/50">
          <div class="flex items-baseline gap-3 mb-5">
            <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
              {{ String(idx + 1).padStart(2, '0') }}
            </span>
            <span class="flex-1 h-px bg-ink-900/10"></span>
            <span class="font-mono text-[10px] tracking-[0.22em] text-ink-500">{{ fmt.extension }}</span>
          </div>

          <div class="flex items-start gap-5 mb-6">
            <div class="w-12 h-12 hairline flex items-center justify-center shrink-0 bg-paper-50">
              <svg v-if="fmt.icon === 'document-text'" class="w-5 h-5 text-ink-900" fill="none" stroke="currentColor" stroke-width="1.25" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <svg v-else-if="fmt.icon === 'code-bracket'" class="w-5 h-5 text-ink-900" fill="none" stroke="currentColor" stroke-width="1.25" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-display italic text-ink-900 text-lg mb-1">{{ fmt.name }}</h3>
              <p class="text-ink-500 text-sm font-serif italic leading-relaxed">{{ fmt.description }}</p>
            </div>
          </div>

          <div class="mt-auto flex gap-3">
            <button @click="previewSkill(fmt.id)" class="btn-ghost flex-1 text-sm flex items-center justify-center gap-2">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.25" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Preview
            </button>
            <button @click="downloadSkill(fmt.id)" class="btn-ink flex-1 text-sm flex items-center justify-center gap-2">
              {{ t('export.download') }} <span class="text-ochre-300">↓</span>
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- ─── Usage Guide ─── -->
    <section class="paper-card-muted p-10">
      <h2 class="rule-heading font-display italic text-ink-900 text-lg mb-8">
        <span class="px-4">{{ t('export.usageGuide') }}</span>
      </h2>
      <div class="grid md:grid-cols-3 gap-8">
        <div v-for="(guide, idx) in guides" :key="idx" class="space-y-2">
          <div class="flex items-baseline gap-3">
            <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
              {{ String(idx + 1).padStart(2, '0') }}
            </span>
            <h3 class="font-display italic text-ink-900">{{ guide.title }}</h3>
          </div>
          <p class="text-ink-700 text-sm font-serif leading-relaxed">{{ guide.desc }}</p>
        </div>
      </div>
      <div class="mt-8 pt-5 hairline-t text-center">
        <a href="https://github.com/username/PersonaLingo" target="_blank"
           class="ink-underline text-ink-500 hover:text-ink-900 text-xs font-mono tracking-[0.22em] transition-colors">
          {{ t('export.viewSource') }}
        </a>
      </div>
    </section>

    <!-- ─── Preview Modal ─── -->
    <teleport to="body">
      <transition name="modal">
        <div v-if="previewVisible" class="fixed inset-0 z-50 flex items-center justify-center p-4"
             @click.self="closePreview" @keydown.esc="closePreview">
          <div class="absolute inset-0 bg-ink-900/40 backdrop-blur-[2px]"></div>

          <div class="relative w-full max-w-4xl max-h-[85vh] bg-paper-50 hairline-strong shadow-[0_20px_60px_-20px_rgba(27,31,42,0.25)] flex flex-col overflow-hidden">
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 hairline-b shrink-0">
              <div class="flex items-baseline gap-3">
                <span class="font-display italic text-ink-900 text-lg">{{ previewFilename }}</span>
                <span class="font-mono text-[10px] tracking-[0.22em] px-2 py-0.5 bg-ochre-300/25 text-ochre-500">
                  {{ previewFormat.toUpperCase() }}
                </span>
              </div>
              <button @click="closePreview"
                      class="w-8 h-8 flex items-center justify-center text-ink-500 hover:text-ink-900 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Code Area -->
            <div class="flex-1 overflow-auto p-6 bg-paper-100/40">
              <pre class="text-sm text-ink-700 font-mono whitespace-pre-wrap leading-relaxed">{{ previewContent }}</pre>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-end gap-3 px-6 py-4 hairline-t shrink-0">
              <button @click="copyToClipboard" class="btn-ghost text-sm flex items-center gap-2">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="1.25" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round"
                        d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3" />
                </svg>
                {{ copied ? t('export.copied') : t('export.copyToClipboard') }}
              </button>
              <button @click="downloadFromPreview" class="btn-ink text-sm flex items-center gap-2">
                {{ t('export.download') }} <span class="text-ochre-300">↓</span>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { exportSkillMarkdown, exportSkillJson, getCorpus } from '../api'
import { useCorpusStore } from '../stores/corpus'
import { useI18n } from '../i18n'

const { t } = useI18n()
const corpusStore = useCorpusStore()

const skillFormats = ref([
  { id: 'markdown', name: 'Markdown Skill File', description: 'For Trae, Cursor, and similar IDE Agents', extension: '.md', icon: 'document-text' },
  { id: 'json', name: 'JSON Schema', description: 'For GPTs, Coze, Dify, and similar platforms', extension: '.json', icon: 'code-bracket' },
])

const guides = computed(() => [
  { title: 'Trae / Cursor', desc: t('export.traeDesc') },
  { title: 'GPTs / Coze / Dify', desc: t('export.gptsDesc') },
  { title: 'API-Capable Agents', desc: t('export.apiDesc') },
])

const previewVisible = ref(false)
const previewContent = ref('')
const previewFilename = ref('')
const previewFormat = ref('')
const previewMimeType = ref('')
const copied = ref(false)
const loading = ref(false)
const corpusCache = ref(null)

onMounted(() => {})

function resolveCorpusId() {
  return corpusStore.currentCorpusId || localStorage.getItem('corpusId') || ''
}

async function fetchSkillContent(formatId) {
  const corpusId = resolveCorpusId()
  if (!corpusId) {
    alert('请先生成语料库再导出 Skill')
    return null
  }
  loading.value = true
  try {
    if (formatId === 'json') {
      const data = await exportSkillJson(corpusId)
      return { content: JSON.stringify(data, null, 2), filename: 'personalingo_skill.json', mime_type: 'application/json' }
    }
    const text = await exportSkillMarkdown(corpusId)
    const content = typeof text === 'string' ? text : JSON.stringify(text, null, 2)
    return { content, filename: 'personalingo_skill.md', mime_type: 'text/markdown' }
  } catch (err) {
    console.error('Export failed:', err)
    alert('Skill 导出失败: ' + (err?.response?.data?.detail || err.message || 'unknown'))
    return null
  } finally {
    loading.value = false
  }
}

async function previewSkill(formatId) {
  const result = await fetchSkillContent(formatId)
  if (!result) return
  previewContent.value = result.content
  previewFilename.value = result.filename
  previewFormat.value = formatId
  previewMimeType.value = result.mime_type
  previewVisible.value = true
  copied.value = false
}

function closePreview() { previewVisible.value = false }

async function downloadSkill(formatId) {
  const result = await fetchSkillContent(formatId)
  if (!result) return
  triggerDownload(result.content, result.filename, result.mime_type)
}

function downloadFromPreview() {
  triggerDownload(previewContent.value, previewFilename.value, previewMimeType.value)
}

async function loadCorpusDataOnce() {
  if (corpusCache.value) return corpusCache.value
  const corpusId = resolveCorpusId()
  if (!corpusId) {
    alert('请先生成语料库再下载')
    return null
  }
  try {
    const res = await getCorpus(corpusId)
    corpusCache.value = res?.data || res
    return corpusCache.value
  } catch (err) {
    console.error('Load corpus failed:', err)
    alert('语料库加载失败: ' + (err?.response?.data?.detail || err.message))
    return null
  }
}

function buildCorpusHtml(corpus) {
  const section = (title, items, renderer) => {
    if (!items || !items.length) return ''
    const body = items.map(renderer).join('\n')
    return `<section><h2>${title}</h2>${body}</section>`
  }
  const escape = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
  const anchorsHtml = section('Anchors', corpus.anchors, (a) => `<div class="card"><h3>${escape(a.label || a.id)}</h3><p>${escape(a.story || '')}</p></div>`)
  const bridgesHtml = section('Bridges', corpus.bridges, (b) => `<div class="card"><strong>${escape(b.topic_title || '')}</strong><p>${escape(b.sample_answer || b.bridge_sentence || '')}</p></div>`)
  const vocabHtml = section('Vocabulary', corpus.vocabulary, (v) => `<div class="card">${escape(v.basic_word || '')} → <strong>${escape(v.upgrade || '')}</strong><br/><em>${escape(v.context || '')}</em></div>`)
  const patternsHtml = section('Patterns', corpus.patterns, (p) => `<div class="card"><strong>${escape(p.name || '')}</strong>: ${escape(p.formula || '')}<br/><em>${escape(p.example || '')}</em></div>`)
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><title>PersonaLingo Corpus</title>
<style>body{font-family:Georgia,'Noto Serif SC',serif;max-width:900px;margin:2.5rem auto;padding:0 1.25rem;color:#1B1F2A;line-height:1.7;background:#FBF7EE}
h1{font-style:italic;border-bottom:1px solid rgba(27,31,42,0.15);padding-bottom:.5rem;font-weight:500;letter-spacing:-0.01em}
h2{margin-top:2.5rem;color:#1E3A8A;font-style:italic;font-weight:500}
.card{background:#F5EFE0;border:1px solid rgba(27,31,42,0.1);padding:1rem 1.2rem;margin:.7rem 0}</style></head>
<body><h1>PersonaLingo · Corpus</h1><p>Corpus ID: ${escape(corpus.id || '')}</p>
${anchorsHtml}${bridgesHtml}${vocabHtml}${patternsHtml}</body></html>`
}

async function downloadCorpus(format) {
  const corpus = await loadCorpusDataOnce()
  if (!corpus) return
  if (format === 'json') {
    triggerDownload(JSON.stringify(corpus, null, 2), 'personalingo_corpus.json', 'application/json')
  } else {
    triggerDownload(buildCorpusHtml(corpus), 'personalingo_corpus.html', 'text/html')
  }
}

function triggerDownload(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(previewContent.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    console.error('Failed to copy')
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s cubic-bezier(.2,.8,.2,1);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
