<template>
  <section id="patterns" class="mb-12">
    <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zm12 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
      </svg>
      Sentence Patterns
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <div
        v-for="(pattern, i) in patterns"
        :key="i"
        class="bg-gray-800 rounded-xl p-5 border border-gray-700/50 transition-all duration-200 hover:border-cyan-500/30 hover:shadow-lg hover:shadow-cyan-500/5"
      >
        <!-- Pattern Name -->
        <h3 class="text-base font-semibold text-white mb-3">{{ pattern.pattern_name }}</h3>

        <!-- Template Formula -->
        <div class="bg-gray-900/50 rounded-lg p-3 mb-3 font-mono text-sm">
          <span v-html="formatTemplate(pattern.template)"></span>
        </div>

        <!-- Example -->
        <div class="mb-3">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Example</h4>
          <p class="text-gray-300 text-sm leading-relaxed" v-html="formatExample(pattern)"></p>
        </div>

        <!-- Usage Context -->
        <p class="text-gray-500 text-xs mb-3">
          <span class="text-gray-400 font-medium">When:</span> {{ pattern.usage_context }}
        </p>

        <!-- MBTI Fit -->
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 bg-purple-500/10 border border-purple-500/30 rounded text-purple-300 text-xs">
            MBTI Fit
          </span>
          <span class="text-gray-400 text-xs">{{ pattern.why_it_fits }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  patterns: {
    type: Array,
    required: true
  }
})

// Format template: highlight [...] variables
function formatTemplate(template) {
  if (!template) return ''
  return template.replace(
    /\[([^\]]+)\]/g,
    '<span class="text-amber-300 bg-amber-500/10 px-1 rounded">[<span class="font-semibold">$1</span>]</span>'
  )
}

// Format example: highlight the filled-in variable parts with cyan
function formatExample(pattern) {
  if (!pattern.example) return ''
  // Try to highlight words that differ from template placeholders
  let example = pattern.example
  // Simple approach: highlight any part that matches keywords from template variables
  const templateVars = pattern.template?.match(/\[([^\]]+)\]/g) || []
  if (templateVars.length > 0) {
    // Find the common prefix/suffix between template and example to highlight differences
    const templateParts = pattern.template.split(/\[[^\]]+\]/)
    let remaining = example
    let result = ''
    for (let k = 0; k < templateParts.length; k++) {
      const part = templateParts[k]
      const idx = remaining.indexOf(part)
      if (idx > 0) {
        result += `<span class="text-cyan-300 font-medium">${remaining.substring(0, idx)}</span>`
        result += part
        remaining = remaining.substring(idx + part.length)
      } else if (idx === 0) {
        result += part
        remaining = remaining.substring(part.length)
      } else {
        result += remaining
        remaining = ''
        break
      }
    }
    if (remaining) {
      result += `<span class="text-cyan-300 font-medium">${remaining}</span>`
    }
    return result || example
  }
  return example
}
</script>
