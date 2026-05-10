<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="flex items-baseline justify-between mb-5 hairline-b pb-4">
      <div>
        <p class="num-chapter">Apparatus &middot; Extractor</p>
        <h3 class="font-display text-xl text-ink-900 tracking-tight mt-1">Index cards</h3>
      </div>
      <span class="font-mono text-[0.68rem] tracking-[0.22em] text-ochre-500 tabular-nums uppercase">
        {{ String(totalItems).padStart(2, '0') }} entries
      </span>
    </div>

    <!-- Extracted Sections -->
    <div class="flex-1 overflow-y-auto space-y-6 pr-1">
      <section
        v-for="(cat, sIdx) in sections"
        :key="cat.key"
      >
        <div class="flex items-baseline justify-between mb-2">
          <h4 class="font-display italic text-[1.08rem] text-ink-900 tracking-tight">
            <span class="text-ochre-500 font-mono not-italic text-[0.7rem] tracking-[0.22em] mr-2 align-middle">
              {{ String(sIdx + 1).padStart(2, '0') }}
            </span>
            {{ cat.label }}
          </h4>
          <span class="font-mono text-[0.66rem] text-ink-300 tabular-nums">
            {{ (items[cat.key] || []).length }}
          </span>
        </div>

        <div class="space-y-2">
          <label
            v-for="(item, idx) in (items[cat.key] || [])"
            :key="cat.key + '-' + idx"
            class="flex items-start gap-3 p-3 hairline cursor-pointer transition-colors hover:bg-paper-100/60 group"
            style="border-radius: 2px;"
          >
            <span class="font-mono text-[0.66rem] text-ochre-500 mt-0.5 tabular-nums shrink-0">
              {{ String(idx + 1).padStart(2, '0') }}
            </span>
            <input
              type="checkbox"
              v-model="selectedItems[cat.key][idx]"
              class="mt-1 accent-ink-900"
            />
            <span class="font-serif text-[0.95rem] text-ink-700 leading-relaxed">
              {{ item }}
            </span>
          </label>
          <p v-if="!(items[cat.key] || []).length" class="font-serif italic text-sm text-ink-300 pl-1">
            &mdash; none extracted yet
          </p>
        </div>
      </section>
    </div>

    <!-- Merge Button -->
    <div class="mt-5 pt-4 hairline-t">
      <button
        @click="handleMerge"
        :disabled="selectedCount === 0"
        class="btn-ink w-full justify-center disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <span class="font-mono text-[0.68rem] tracking-[0.24em] uppercase">
          Merge {{ String(selectedCount).padStart(2, '0') }} to corpus
        </span>
        <svg class="arrow w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" d="M5 12h14m0 0l-6-6m6 6l-6 6" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'

const props = defineProps({
  items: {
    type: Object,
    default: () => ({ anchors: [], vocabulary: [], bridges: [], patterns: [] })
  }
})

const emit = defineEmits(['merge'])

const sections = [
  { key: 'anchors',    label: 'Anchors'    },
  { key: 'vocabulary', label: 'Vocabulary' },
  { key: 'bridges',    label: 'Bridges'    },
  { key: 'patterns',   label: 'Patterns'   }
]

const selectedItems = reactive({
  anchors: {}, vocabulary: {}, bridges: {}, patterns: {}
})

const totalItems = computed(() => {
  const { anchors = [], vocabulary = [], bridges = [], patterns = [] } = props.items
  return anchors.length + vocabulary.length + bridges.length + patterns.length
})

const selectedCount = computed(() => {
  let count = 0
  for (const category of Object.keys(selectedItems)) {
    for (const key of Object.keys(selectedItems[category])) {
      if (selectedItems[category][key]) count++
    }
  }
  return count
})

function handleMerge() {
  const merged = { anchors: [], vocabulary: [], bridges: [], patterns: [] }
  for (const category of Object.keys(selectedItems)) {
    for (const [idx, checked] of Object.entries(selectedItems[category])) {
      if (checked && props.items[category]?.[idx]) {
        merged[category].push(props.items[category][idx])
      }
    }
  }
  emit('merge', merged)
}
</script>
