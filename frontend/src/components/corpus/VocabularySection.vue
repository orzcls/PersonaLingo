<template>
  <section id="vocabulary" class="mb-12">
    <h2 class="text-2xl font-bold text-white mb-4 flex items-center gap-2">
      <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
      </svg>
      Vocabulary Upgrade
    </h2>

    <!-- View Toggle -->
    <div class="flex items-center gap-2 mb-6">
      <button
        @click="viewMode = 'card'"
        class="p-2 rounded-lg transition-colors duration-200"
        :class="viewMode === 'card' ? 'bg-cyan-500/20 text-cyan-300' : 'text-gray-500 hover:text-gray-300'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      </button>
      <button
        @click="viewMode = 'table'"
        class="p-2 rounded-lg transition-colors duration-200"
        :class="viewMode === 'table' ? 'bg-cyan-500/20 text-cyan-300' : 'text-gray-500 hover:text-gray-300'"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
      </button>
    </div>

    <!-- Card View -->
    <div v-if="viewMode === 'card'">
      <div v-for="(group, category) in groupedVocab" :key="category" class="mb-8">
        <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
          <span class="w-2 h-2 bg-cyan-400 rounded-full"></span>
          {{ category }}
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(item, i) in group"
            :key="i"
            class="bg-gray-800 rounded-xl p-4 transition-all duration-200 hover:bg-gray-750"
          >
            <!-- Word upgrade arrow -->
            <div class="flex items-center gap-3 mb-3">
              <span class="text-gray-500 line-through text-sm">{{ item.basic_word }}</span>
              <svg class="w-4 h-4 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="(alt, j) in item.advanced_alternatives"
                  :key="j"
                  class="px-2 py-0.5 bg-cyan-500/10 border border-cyan-500/30 rounded text-cyan-300 text-sm font-medium"
                >
                  {{ alt }}
                </span>
              </div>
            </div>

            <!-- Example sentence with highlighted word -->
            <p class="text-gray-400 text-sm leading-relaxed" v-html="highlightExample(item)"></p>

            <!-- Anchor context -->
            <div class="mt-2 flex items-center gap-2">
              <span
                class="px-1.5 py-0.5 rounded text-xs font-bold"
                :class="anchorBadge(item.anchor_context)"
              >
                {{ item.anchor_context }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-700">
            <th class="text-left py-3 px-4 text-gray-400 font-medium">Basic</th>
            <th class="text-left py-3 px-4 text-gray-400 font-medium">Upgrades</th>
            <th class="text-left py-3 px-4 text-gray-400 font-medium">Example</th>
            <th class="text-left py-3 px-4 text-gray-400 font-medium">Category</th>
            <th class="text-left py-3 px-4 text-gray-400 font-medium">Anchor</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, i) in vocabulary"
            :key="i"
            class="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
          >
            <td class="py-3 px-4 text-gray-500 line-through">{{ item.basic_word }}</td>
            <td class="py-3 px-4">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="(alt, j) in item.advanced_alternatives"
                  :key="j"
                  class="px-1.5 py-0.5 bg-cyan-500/10 rounded text-cyan-300 text-xs"
                >
                  {{ alt }}
                </span>
              </div>
            </td>
            <td class="py-3 px-4 text-gray-400 max-w-xs truncate">{{ item.example_sentence }}</td>
            <td class="py-3 px-4 text-gray-500 text-xs">{{ item.category }}</td>
            <td class="py-3 px-4">
              <span class="px-1.5 py-0.5 rounded text-xs font-bold" :class="anchorBadge(item.anchor_context)">
                {{ item.anchor_context }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  vocabulary: {
    type: Array,
    required: true
  }
})

const viewMode = ref('card')

const groupedVocab = computed(() => {
  const groups = {}
  props.vocabulary.forEach(item => {
    if (!groups[item.category]) groups[item.category] = []
    groups[item.category].push(item)
  })
  return groups
})

function highlightExample(item) {
  let sentence = item.example_sentence || ''
  // Highlight advanced alternatives in the example
  item.advanced_alternatives.forEach(word => {
    const regex = new RegExp(`(${word})`, 'gi')
    sentence = sentence.replace(regex, '<span class="text-cyan-300 font-medium">$1</span>')
  })
  return sentence
}

const anchorBadge = (id) => {
  const colors = {
    A: 'bg-cyan-500/20 text-cyan-300',
    B: 'bg-purple-500/20 text-purple-300',
    C: 'bg-amber-500/20 text-amber-300',
    D: 'bg-emerald-500/20 text-emerald-300'
  }
  return colors[id] || 'bg-gray-700 text-gray-300'
}
</script>
