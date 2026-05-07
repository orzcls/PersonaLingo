<template>
  <div class="max-w-7xl mx-auto px-4 py-12">
    <!-- Page Header -->
    <div class="text-center mb-14">
      <h1 class="text-4xl font-bold text-white mb-4">Export Your Corpus & Skills</h1>
      <p class="text-dark-400 text-lg max-w-2xl mx-auto">
        Download your personalized corpus or export reusable AI Agent Skill files for any platform.
      </p>
    </div>

    <!-- ─── Corpus Download Section ─── -->
    <section class="mb-16">
      <h2 class="text-xl font-semibold text-white mb-6 flex items-center gap-2">
        <svg class="w-5 h-5 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        Download Corpus
      </h2>
      <div class="grid md:grid-cols-2 gap-6">
        <!-- HTML Download -->
        <div class="group bg-dark-800/60 border border-dark-700 rounded-xl p-6 hover:border-secondary-500/40 transition-all">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-secondary-500/10 rounded-lg flex items-center justify-center shrink-0">
              <svg class="w-6 h-6 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-white font-medium mb-1">HTML File</h3>
              <p class="text-dark-400 text-sm mb-4">Standalone HTML page — open in any browser, works offline.</p>
              <button @click="downloadCorpus('html')"
                class="inline-flex items-center gap-2 px-4 py-2 bg-secondary-600 hover:bg-secondary-500 text-white text-sm font-medium rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download .html
              </button>
            </div>
          </div>
        </div>
        <!-- JSON Download -->
        <div class="group bg-dark-800/60 border border-dark-700 rounded-xl p-6 hover:border-secondary-500/40 transition-all">
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 bg-secondary-500/10 rounded-lg flex items-center justify-center shrink-0">
              <svg class="w-6 h-6 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-white font-medium mb-1">JSON Data</h3>
              <p class="text-dark-400 text-sm mb-4">Raw structured data — ideal for programmatic use or further processing.</p>
              <button @click="downloadCorpus('json')"
                class="inline-flex items-center gap-2 px-4 py-2 bg-secondary-600 hover:bg-secondary-500 text-white text-sm font-medium rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download .json
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── Skill Export Section (Core Highlight) ─── -->
    <section class="mb-16">
      <h2 class="text-xl font-semibold text-white mb-2 flex items-center gap-2">
        <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Export AI Agent Skill
      </h2>
      <p class="text-dark-400 text-sm mb-6">
        Package the entire questionnaire → corpus generation workflow as a reusable Skill file for any AI Agent platform.
      </p>

      <div class="grid md:grid-cols-3 gap-6">
        <div v-for="fmt in skillFormats" :key="fmt.id"
          class="group bg-dark-800/60 border border-dark-700 rounded-xl p-6 hover:border-accent-500/40 transition-all flex flex-col">
          <!-- Icon -->
          <div class="w-12 h-12 bg-accent-500/10 rounded-lg flex items-center justify-center mb-4">
            <svg v-if="fmt.icon === 'document-text'" class="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <svg v-else-if="fmt.icon === 'code-bracket'" class="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            <svg v-else class="w-6 h-6 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
            </svg>
          </div>

          <!-- Info -->
          <h3 class="text-white font-semibold text-lg mb-1">{{ fmt.name }}</h3>
          <p class="text-dark-400 text-sm mb-1">{{ fmt.description }}</p>
          <span class="text-accent-400/70 text-xs font-mono mb-5">{{ fmt.extension }}</span>

          <!-- Actions -->
          <div class="mt-auto flex gap-3">
            <button @click="previewSkill(fmt.id)"
              class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 border border-dark-600 hover:border-accent-500/50 text-dark-300 hover:text-white text-sm rounded-lg transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Preview
            </button>
            <button @click="downloadSkill(fmt.id)"
              class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 bg-accent-600 hover:bg-accent-500 text-white text-sm font-medium rounded-lg transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ─── Usage Guide ─── -->
    <section class="bg-dark-800/40 border border-dark-700 rounded-xl p-8">
      <h2 class="text-lg font-semibold text-white mb-4">How to Use Exported Skills</h2>
      <div class="grid md:grid-cols-3 gap-6 text-sm">
        <div>
          <h3 class="text-accent-400 font-medium mb-2">Trae / Cursor</h3>
          <p class="text-dark-400 leading-relaxed">
            Place the <code class="text-accent-300 bg-dark-900/60 px-1.5 py-0.5 rounded">.md</code> file in your project's
            <code class="text-accent-300 bg-dark-900/60 px-1.5 py-0.5 rounded">.trae/skills/</code> or rules directory. The agent will automatically discover and use it.
          </p>
        </div>
        <div>
          <h3 class="text-accent-400 font-medium mb-2">GPTs / Coze / Dify</h3>
          <p class="text-dark-400 leading-relaxed">
            Upload the <code class="text-accent-300 bg-dark-900/60 px-1.5 py-0.5 rounded">.json</code> file as a skill definition or paste it into your agent's configuration panel.
          </p>
        </div>
        <div>
          <h3 class="text-accent-400 font-medium mb-2">API-Capable Agents</h3>
          <p class="text-dark-400 leading-relaxed">
            Import the <code class="text-accent-300 bg-dark-900/60 px-1.5 py-0.5 rounded">.yaml</code> OpenAPI spec. The agent can call PersonaLingo APIs directly.
          </p>
        </div>
      </div>
      <div class="mt-6 pt-4 border-t border-dark-700">
        <a href="https://github.com/username/PersonaLingo" target="_blank"
          class="text-dark-500 hover:text-accent-400 text-xs transition-colors">
          View source on GitHub →
        </a>
      </div>
    </section>

    <!-- ─── Preview Modal ─── -->
    <teleport to="body">
      <transition name="modal">
        <div v-if="previewVisible" class="fixed inset-0 z-50 flex items-center justify-center p-4"
          @click.self="closePreview" @keydown.esc="closePreview">
          <!-- Backdrop -->
          <div class="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>

          <!-- Modal Content -->
          <div class="relative w-full max-w-4xl max-h-[85vh] bg-dark-900 border border-dark-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-dark-700 shrink-0">
              <div class="flex items-center gap-3">
                <span class="text-white font-semibold">{{ previewFilename }}</span>
                <span class="text-xs font-mono px-2 py-0.5 bg-accent-500/10 text-accent-400 rounded">
                  {{ previewFormat.toUpperCase() }}
                </span>
              </div>
              <button @click="closePreview"
                class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Code Area -->
            <div class="flex-1 overflow-auto p-6">
              <pre class="text-sm text-dark-300 font-mono whitespace-pre-wrap leading-relaxed">{{ previewContent }}</pre>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-dark-700 shrink-0">
              <button @click="copyToClipboard"
                class="inline-flex items-center gap-2 px-4 py-2 border border-dark-600 hover:border-accent-500/50 text-dark-300 hover:text-white text-sm rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                {{ copied ? 'Copied!' : 'Copy to Clipboard' }}
              </button>
              <button @click="downloadFromPreview"
                class="inline-flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-500 text-white text-sm font-medium rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSkillFormats, exportSkill } from '../api'

// ─── State ───
const skillFormats = ref([])
const previewVisible = ref(false)
const previewContent = ref('')
const previewFilename = ref('')
const previewFormat = ref('')
const previewMimeType = ref('')
const copied = ref(false)
const loading = ref(false)

// ─── Lifecycle ───
onMounted(async () => {
  try {
    const res = await getSkillFormats()
    skillFormats.value = res.formats || []
  } catch (err) {
    console.error('Failed to load skill formats:', err)
    // Fallback formats
    skillFormats.value = [
      { id: 'markdown', name: 'Markdown Skill File', description: 'For Trae, Cursor, and similar IDE Agents', extension: '.md', icon: 'document-text' },
      { id: 'json', name: 'JSON Schema', description: 'For GPTs, Coze, Dify, and similar platforms', extension: '.json', icon: 'code-bracket' },
      { id: 'openapi', name: 'OpenAPI Specification', description: 'For Agents with API calling capabilities', extension: '.yaml', icon: 'globe-alt' },
    ]
  }
})

// ─── Skill Export ───
async function fetchSkillContent(formatId) {
  loading.value = true
  try {
    const res = await exportSkill(formatId)
    return res
  } catch (err) {
    console.error('Export failed:', err)
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

function closePreview() {
  previewVisible.value = false
}

async function downloadSkill(formatId) {
  const result = await fetchSkillContent(formatId)
  if (!result) return
  triggerDownload(result.content, result.filename, result.mime_type)
}

function downloadFromPreview() {
  triggerDownload(previewContent.value, previewFilename.value, previewMimeType.value)
}

// ─── Corpus Download (placeholder) ───
function downloadCorpus(format) {
  // Placeholder: in production this would fetch real corpus data
  const placeholder = format === 'json'
    ? JSON.stringify({ message: 'Corpus data placeholder — generate a corpus first.' }, null, 2)
    : '<html><body><h1>PersonaLingo Corpus</h1><p>Generate a corpus first to see content here.</p></body></html>'
  const ext = format === 'json' ? '.json' : '.html'
  const mime = format === 'json' ? 'application/json' : 'text/html'
  triggerDownload(placeholder, `personalingo_corpus${ext}`, mime)
}

// ─── Utilities ───
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
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
