<template>
  <section class="mb-8">
    <div class="relative overflow-hidden bg-gradient-to-br from-gray-800 via-gray-800 to-gray-900 rounded-xl border border-gray-700/50 p-6 md:p-8">
      <!-- Background decoration -->
      <div class="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/5 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>

      <div class="relative z-10">
        <!-- Top row: MBTI + Target Score -->
        <div class="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span class="text-2xl font-black text-white tracking-tight">{{ persona.mbti_type }}</span>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">{{ persona.mbti_type }}</h2>
              <p class="text-gray-400 text-sm mt-0.5">{{ persona.mbti_description }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-400 text-sm font-semibold">
              🎯 Target: Band {{ persona.target_score }}
            </span>
            <span v-if="persona.exam_date" class="px-3 py-1.5 bg-gray-700/50 border border-gray-600/50 rounded-lg text-gray-300 text-sm">
              📅 {{ persona.exam_date }}
            </span>
          </div>
        </div>

        <!-- Communication Style -->
        <div class="mb-5">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Communication Style</h3>
          <p class="text-gray-300 text-sm leading-relaxed">{{ persona.communication_style }}</p>
        </div>

        <!-- Interest Tags -->
        <div class="mb-5">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Interests</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(tag, i) in persona.interest_tags"
              :key="i"
              class="px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-full text-cyan-300 text-sm font-medium transition-colors hover:bg-cyan-500/20"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Topic Focus -->
        <div v-if="persona.topic_focus && persona.topic_focus.length">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Topic Focus</h3>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(topic, i) in persona.topic_focus"
              :key="i"
              class="px-2.5 py-1 bg-purple-500/10 border border-purple-500/30 rounded-full text-purple-300 text-xs font-medium"
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
  persona: {
    type: Object,
    required: true
  }
})
</script>
