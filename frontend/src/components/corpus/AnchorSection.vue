<template>
  <section id="anchors" class="mb-12">
    <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      Anchor Stories
    </h2>

    <div class="grid gap-6">
      <div
        v-for="anchor in anchors"
        :key="anchor.id"
        class="bg-gray-800 rounded-xl p-6 border-l-4 transition-all duration-200 hover:shadow-lg hover:shadow-black/20"
        :class="borderColor(anchor.id)"
      >
        <!-- Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <span
              class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
              :class="badgeColor(anchor.id)"
            >
              {{ anchor.id }}
            </span>
            <h3 class="text-lg font-semibold text-white">{{ anchor.title }}</h3>
          </div>
        </div>

        <!-- Core Story -->
        <p class="text-gray-300 leading-relaxed mb-4">{{ anchor.core_story }}</p>

        <!-- Keywords -->
        <div class="mb-4">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Keywords</h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(kw, i) in anchor.keywords"
              :key="i"
              class="px-2.5 py-0.5 bg-gray-700/50 border border-gray-600/50 rounded-full text-gray-300 text-xs"
            >
              {{ kw }}
            </span>
          </div>
        </div>

        <!-- Emotions -->
        <div class="mb-4">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Emotions</h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(em, i) in anchor.emotions"
              :key="i"
              class="px-2.5 py-0.5 bg-pink-500/10 border border-pink-500/30 rounded-full text-pink-300 text-xs"
            >
              {{ em }}
            </span>
          </div>
        </div>

        <!-- Versatility Topics -->
        <div>
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Can Connect To</h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(topic, i) in anchor.versatility_topics"
              :key="i"
              class="px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="topicTagColor(anchor.id)"
            >
              {{ topic }}
            </span>
          </div>
        </div>
      </div>
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

const anchorColors = {
  A: { border: 'border-cyan-400', badge: 'bg-cyan-500/20 text-cyan-300', topic: 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20' },
  B: { border: 'border-purple-400', badge: 'bg-purple-500/20 text-purple-300', topic: 'bg-purple-500/10 text-purple-300 border border-purple-500/20' },
  C: { border: 'border-amber-400', badge: 'bg-amber-500/20 text-amber-300', topic: 'bg-amber-500/10 text-amber-300 border border-amber-500/20' },
  D: { border: 'border-emerald-400', badge: 'bg-emerald-500/20 text-emerald-300', topic: 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20' }
}

function borderColor(id) {
  return anchorColors[id]?.border || 'border-gray-600'
}

function badgeColor(id) {
  return anchorColors[id]?.badge || 'bg-gray-700 text-gray-300'
}

function topicTagColor(id) {
  return anchorColors[id]?.topic || 'bg-gray-700/50 text-gray-300'
}
</script>
