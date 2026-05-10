<template>
  <div class="flex flex-wrap items-center gap-x-8 gap-y-3">
    <!-- Part Filter -->
    <div class="flex items-center gap-1">
      <span class="field-label mr-3">Part</span>
      <button
        v-for="part in partOptions"
        :key="part"
        @click="updateFilter('part', part)"
        class="filter-chip"
        :class="filters.part === part ? 'is-active' : ''"
      >
        {{ part }}
      </button>
    </div>

    <!-- Season Filter -->
    <div class="flex items-center gap-1">
      <span class="field-label mr-3">Season</span>
      <button
        v-for="season in seasonOptions"
        :key="season"
        @click="updateFilter('season', season)"
        class="filter-chip"
        :class="filters.season === season ? 'is-active' : ''"
      >
        {{ season }}
      </button>
    </div>

    <!-- Category Filter -->
    <div class="flex items-center gap-1 flex-wrap">
      <span class="field-label mr-3">Category</span>
      <button
        v-for="cat in categoryOptions"
        :key="cat"
        @click="updateFilter('category', cat)"
        class="filter-chip"
        :class="filters.category === cat ? 'is-active' : ''"
      >
        {{ cat }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getTopicSeasons } from '../../api'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['filter-change'])

const partOptions = ['All', 'P1', 'P2', 'P3']
const categoryOptions = ['All', 'hobby_leisure', 'person', 'place', 'event', 'object', 'abstract']

// Season 选项从 API 动态拉取，后端返回 DISTINCT season DESC
const remoteSeasons = ref([])
const seasonOptions = computed(() => ['All', ...remoteSeasons.value])

onMounted(async () => {
  try {
    const resp = await getTopicSeasons()
    const list = resp.data || []
    remoteSeasons.value = Array.isArray(list) ? list.filter(Boolean) : []
  } catch (e) {
    console.warn('Failed to fetch topic seasons:', e)
    remoteSeasons.value = []
  }
})

function updateFilter(key, value) {
  emit('filter-change', { ...props.filters, [key]: value })
}
</script>

<style scoped>
.filter-chip {
  padding: 0.25rem 0.6rem;
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 13px;
  color: var(--ink-500, #5F6572);
  letter-spacing: 0.01em;
  transition: color .2s ease, background .2s ease;
  position: relative;
}
.filter-chip:hover {
  color: var(--ink-900, #1B1F2A);
}
.filter-chip.is-active {
  color: var(--paper-50, #FBF7EE);
  background: var(--ink-900, #1B1F2A);
  /* Align with chip-ink-selected: ochre edge-tab + corner mark */
  box-shadow: inset 3px 0 0 0 var(--ochre-500, #B8692B);
  padding-left: calc(0.6rem + 3px);
  font-weight: 500;
}
.filter-chip.is-active::after {
  content: '';
  position: absolute;
  top: 3px;
  right: 3px;
  width: 5px;
  height: 5px;
  border-right: 1px solid var(--ochre-300, #E3B98E);
  border-top: 1px solid var(--ochre-300, #E3B98E);
  opacity: .85;
}
</style>
