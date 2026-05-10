<template>
  <section id="patterns" class="mb-16 stagger">
    <header class="mb-7">
      <p class="num-chapter text-[11px] mb-2">§ 04 · syntax</p>
      <h2 class="font-display italic text-3xl md:text-4xl text-ink-900 leading-tight">
        Sentence Patterns
      </h2>
      <p class="mt-2 font-serif text-sm text-ink-500 italic max-w-xl">
        Re-usable scaffolding — slot your own vocabulary into the marked apertures.
      </p>
      <div class="hairline mt-5"></div>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <article
        v-for="(pattern, i) in patterns"
        :key="i"
        class="paper-card p-6"
      >
        <div class="flex items-baseline gap-3 mb-4">
          <span class="num-chapter text-[10px]">{{ String(i + 1).padStart(2, '0') }}</span>
          <h3 class="font-display italic text-xl text-ink-900 flex-1 leading-tight">
            {{ pattern.pattern_name }}
          </h3>
        </div>

        <!-- Template Formula -->
        <div class="border-t border-b border-ink-900/15 py-3 px-1 mb-4 bg-paper-100/40">
          <span class="font-mono text-[13px] leading-relaxed text-ink-700" v-html="formatTemplate(pattern.template)"></span>
        </div>

        <!-- Example -->
        <div class="mb-4">
          <p class="field-label mb-1.5">Example</p>
          <p class="font-serif italic text-[15px] leading-[1.8] text-ink-700" v-html="formatExample(pattern)"></p>
        </div>

        <!-- Usage Context -->
        <div class="mb-3">
          <p class="field-label mb-1">When</p>
          <p class="font-serif text-[13px] text-ink-500 leading-relaxed">{{ pattern.usage_context }}</p>
        </div>

        <div class="hairline mb-3"></div>

        <!-- MBTI Fit -->
        <div class="flex items-start gap-3">
          <span class="font-mono text-[10px] text-ochre-500 tracking-widest shrink-0 pt-0.5">MBTI·FIT</span>
          <span class="font-serif italic text-[13px] text-ink-500 leading-relaxed">{{ pattern.why_it_fits }}</span>
        </div>
      </article>
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

// Format template: highlight [...] variables —— ochre 下划线
function formatTemplate(template) {
  if (!template) return ''
  return template.replace(
    /\[([^\]]+)\]/g,
    '<span style="color:#C3822F;border-bottom:1px dashed #C3822F;padding:0 2px;font-style:italic">$1</span>'
  )
}

// Format example: highlight differences against template —— indigo
function formatExample(pattern) {
  if (!pattern.example) return ''
  let example = pattern.example
  const templateVars = pattern.template?.match(/\[([^\]]+)\]/g) || []
  if (templateVars.length > 0) {
    const templateParts = pattern.template.split(/\[[^\]]+\]/)
    let remaining = example
    let result = ''
    for (let k = 0; k < templateParts.length; k++) {
      const part = templateParts[k]
      const idx = remaining.indexOf(part)
      if (idx > 0) {
        result += `<span style="color:#1E3A8A;font-weight:500;border-bottom:1px solid #1E3A8A">${remaining.substring(0, idx)}</span>`
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
      result += `<span style="color:#1E3A8A;font-weight:500;border-bottom:1px solid #1E3A8A">${remaining}</span>`
    }
    return result || example
  }
  return example
}
</script>
