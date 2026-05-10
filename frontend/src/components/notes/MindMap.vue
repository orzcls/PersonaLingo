<template>
  <div ref="mermaidContainer" class="mermaid-wrapper bg-paper-50 border border-ink-900/15 p-5 overflow-x-auto">
    <div v-if="loading" class="flex items-center justify-center py-10">
      <div class="flex items-end gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-ink-900 animate-ink-diffuse-sm"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-ink-900 animate-ink-diffuse-sm" style="animation-delay:.2s"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-ink-900 animate-ink-diffuse-sm" style="animation-delay:.4s"></span>
      </div>
    </div>
    <div v-else-if="error" class="text-center py-8">
      <p class="font-serif italic text-ink-500 text-sm">Mind map could not be rendered.</p>
      <pre class="mt-3 font-mono text-[11px] text-ink-500 bg-paper-100 border border-ink-900/10 p-3 overflow-x-auto text-left">{{ mermaidCode }}</pre>
    </div>
    <div v-else ref="diagramEl" class="mermaid-diagram flex justify-center"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  mermaidCode: {
    type: String,
    default: ''
  }
})

const mermaidContainer = ref(null)
const diagramEl = ref(null)
const loading = ref(true)
const error = ref(false)

let mermaidInstance = null

async function loadMermaid() {
  if (window.mermaid) {
    mermaidInstance = window.mermaid
    return
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'
    script.onload = () => {
      mermaidInstance = window.mermaid
      // Soft Scholar 主题：象牙白底 · 靛青主色 · 赭石强调
      mermaidInstance.initialize({
        startOnLoad: false,
        theme: 'base',
        fontFamily: 'Fraunces, "Noto Serif SC", Georgia, serif',
        themeVariables: {
          background: '#FBF7EE',
          primaryColor: '#FBF7EE',
          primaryTextColor: '#1B1F2A',
          primaryBorderColor: '#1E3A8A',
          lineColor: '#C3822F',
          secondaryColor: '#F3EBD9',
          tertiaryColor: '#ECE2CC',
          mainBkg: '#FBF7EE',
          nodeBorder: '#1E3A8A',
          clusterBkg: '#F3EBD9',
          clusterBorder: '#C3822F',
          edgeLabelBackground: '#FBF7EE',
          fontSize: '14px'
        }
      })
      resolve()
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

async function renderDiagram() {
  if (!props.mermaidCode) {
    loading.value = false
    return
  }

  loading.value = true
  error.value = false

  try {
    await loadMermaid()
    await nextTick()

    if (diagramEl.value && mermaidInstance) {
      const id = `mermaid-${Date.now()}`
      const { svg } = await mermaidInstance.render(id, props.mermaidCode)
      diagramEl.value.innerHTML = svg
    }
  } catch (e) {
    console.error('Mermaid render error:', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  renderDiagram()
})

watch(() => props.mermaidCode, () => {
  renderDiagram()
})
</script>

<style scoped>
.mermaid-diagram :deep(svg) {
  max-width: 100%;
  height: auto;
}
@keyframes ink-diffuse-sm {
  0% { transform: scale(.6); opacity: .3; }
  50% { transform: scale(1.4); opacity: .9; }
  100% { transform: scale(.6); opacity: .3; }
}
.animate-ink-diffuse-sm {
  animation: ink-diffuse-sm 1.2s cubic-bezier(.4,0,.2,1) infinite;
}
</style>
