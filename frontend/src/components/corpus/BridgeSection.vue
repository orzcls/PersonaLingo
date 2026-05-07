<template>
  <section id="bridges" class="mb-12">
    <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-2">
      <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
      </svg>
      Topic Bridges
    </h2>

    <!-- Category Filter -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        @click="activeCategory = 'all'"
        class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200"
        :class="activeCategory === 'all' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-gray-800 text-gray-400 border border-gray-700 hover:text-gray-200'"
      >
        All
      </button>
      <button
        v-for="cat in categories"
        :key="cat"
        @click="activeCategory = cat"
        class="px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200"
        :class="activeCategory === cat ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'bg-gray-800 text-gray-400 border border-gray-700 hover:text-gray-200'"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Bridge List -->
    <div class="space-y-4">
      <div
        v-for="(bridge, i) in filteredBridges"
        :key="i"
        class="bg-gray-800 rounded-xl p-5 transition-all duration-200 hover:bg-gray-800/80"
      >
        <!-- Topic Question + Anchor Badge -->
        <div class="flex flex-wrap items-center gap-3 mb-3">
          <h3 class="text-base font-semibold text-white flex-1">{{ bridge.topic }}</h3>
          <span
            class="px-2 py-0.5 rounded text-xs font-bold"
            :class="anchorBadge(bridge.anchor_id)"
          >
            Anchor {{ bridge.anchor_id }}
          </span>
          <span class="px-2 py-0.5 bg-gray-700/50 rounded text-xs text-gray-400">
            {{ bridge.category }}
          </span>
        </div>

        <!-- Bridge Sentence -->
        <p class="text-cyan-300/80 italic text-sm mb-3 pl-3 border-l-2 border-cyan-500/30">
          "{{ bridge.bridge_sentence }}"
        </p>

        <!-- Key Phrases -->
        <div class="flex flex-wrap gap-2 mb-3">
          <span
            v-for="(phrase, j) in bridge.key_phrases"
            :key="j"
            class="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-300 text-xs"
          >
            {{ phrase }}
          </span>
        </div>

        <!-- Expandable Sample Answer -->
        <div>
          <button
            @click="toggleExpand(i)"
            class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-cyan-300 transition-colors duration-200"
          >
            <svg
              class="w-4 h-4 transition-transform duration-200"
              :class="{ 'rotate-90': expandedItems[i] }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            {{ expandedItems[i] ? 'Hide' : 'Show' }} Sample Answer
          </button>
          <transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-96"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 max-h-96"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="expandedItems[i]" class="mt-3 pl-4 border-l-2 border-gray-700 overflow-hidden">
              <p class="text-gray-300 text-sm leading-relaxed">{{ bridge.sample_answer }}</p>
            </div>
          </transition>
        </div>
      </div>
    </div>

    <p v-if="filteredBridges.length === 0" class="text-gray-500 text-center py-8">
      No bridges found for this category.
    </p>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  bridges: {
    type: Array,
    required: true
  }
})

const activeCategory = ref('all')
const expandedItems = ref({})

const categories = computed(() => {
  const cats = new Set(props.bridges.map(b => b.category))
  return [...cats]
})

const filteredBridges = computed(() => {
  if (activeCategory.value === 'all') return props.bridges
  return props.bridges.filter(b => b.category === activeCategory.value)
})

function toggleExpand(index) {
  expandedItems.value[index] = !expandedItems.value[index]
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
