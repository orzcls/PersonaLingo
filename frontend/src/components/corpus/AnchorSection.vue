<template>
  <section id="anchors" class="mb-16 stagger">
    <header class="mb-7">
      <p class="num-chapter text-[11px] mb-2">§ 01 · foundation</p>
      <h2 class="font-display italic text-3xl md:text-4xl text-ink-900 leading-tight">
        Anchor Stories
      </h2>
      <p class="mt-2 font-serif text-sm text-ink-500 italic max-w-xl">
        Four recurring narratives you return to, each versatile enough to pivot across many examiner questions.
      </p>
      <div class="hairline mt-5"></div>
    </header>

    <div class="grid gap-5">
      <article
        v-for="anchor in anchors"
        :key="anchor.id"
        class="paper-card p-6 md:p-7 relative overflow-hidden group"
      >
        <!-- 左侧大字母 -->
        <span
          class="absolute -left-1 top-4 font-display italic font-light text-[4.5rem] leading-none pointer-events-none select-none"
          :class="letterColor(anchor.id)"
          style="opacity:.18"
        >{{ anchor.id }}</span>

        <div class="relative pl-16">
          <div class="flex items-baseline gap-3 mb-3">
            <span class="num-chapter text-[10px]">anchor · {{ anchor.id }}</span>
            <span class="hairline flex-1"></span>
          </div>
          <h3 class="font-display italic text-2xl text-ink-900 leading-tight mb-4">
            {{ anchor.title }}
          </h3>

          <!-- Core Story -->
          <p class="font-serif text-[15px] leading-[1.85] text-ink-700 mb-5">
            {{ anchor.core_story }}
          </p>

          <!-- Keywords -->
          <div class="mb-4">
            <p class="field-label mb-2">Keywords</p>
            <div class="flex flex-wrap gap-x-4 gap-y-1">
              <span
                v-for="(kw, i) in anchor.keywords"
                :key="i"
                class="font-mono text-[12px] text-ink-700 tracking-wide"
              >
                {{ kw }}<span v-if="i !== anchor.keywords.length - 1" class="text-ochre-500 ml-3">·</span>
              </span>
            </div>
          </div>

          <!-- Emotions -->
          <div class="mb-4">
            <p class="field-label mb-2">Emotions</p>
            <div class="flex flex-wrap gap-x-2 gap-y-1">
              <span
                v-for="(em, i) in anchor.emotions"
                :key="i"
                class="font-serif italic text-[13px] text-rouge-600"
              >
                {{ em }}<span v-if="i !== anchor.emotions.length - 1" class="text-ink-300">,</span>
              </span>
            </div>
          </div>

          <!-- Versatility Topics -->
          <div>
            <p class="field-label mb-2">Can Connect To</p>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="(topic, i) in anchor.versatility_topics"
                :key="i"
                class="px-2.5 py-0.5 border border-ink-900/15 text-ink-700 text-[12px] font-serif"
              >
                {{ topic }}
              </span>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  anchors: {
    type: Array,
    required: true
  }
})

// 学院色谱替换霓虹配色
const letterColors = {
  A: 'text-indigo-800',
  B: 'text-ochre-500',
  C: 'text-sage-500',
  D: 'text-rouge-600'
}

function letterColor(id) {
  return letterColors[id] || 'text-ink-500'
}
</script>
