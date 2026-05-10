<template>
  <section id="bridges" class="mb-16 stagger">
    <header class="mb-7">
      <p class="num-chapter text-[11px] mb-2">§ 02 · transitions</p>
      <h2 class="font-display italic text-3xl md:text-4xl text-ink-900 leading-tight">
        Topic Bridges
      </h2>
      <p class="mt-2 font-serif text-sm text-ink-500 italic max-w-xl">
        Sentences that carry an anchor into unfamiliar topic waters.
      </p>
      <div class="hairline mt-5"></div>
    </header>

    <!-- Category Filter —— 章节式下划线切换 -->
    <nav class="flex flex-wrap items-center gap-x-6 gap-y-2 mb-8">
      <button
        @click="activeCategory = 'all'"
        class="tab-link font-serif italic text-[15px] transition-colors"
        :class="activeCategory === 'all' ? 'text-ink-900 is-active' : 'text-ink-500 hover:text-ink-700'"
      >
        <span class="font-mono text-ochre-500 text-[10px] tracking-widest not-italic mr-1.5">00</span>All
      </button>
      <button
        v-for="(cat, idx) in categories"
        :key="cat"
        @click="activeCategory = cat"
        class="tab-link font-serif italic text-[15px] transition-colors"
        :class="activeCategory === cat ? 'text-ink-900 is-active' : 'text-ink-500 hover:text-ink-700'"
      >
        <span class="font-mono text-ochre-500 text-[10px] tracking-widest not-italic mr-1.5">{{ String(idx + 1).padStart(2, '0') }}</span>{{ cat }}
      </button>
    </nav>

    <!-- Bridge List -->
    <div class="space-y-5">
      <article
        v-for="(bridge, i) in filteredBridges"
        :key="i"
        class="paper-card p-6"
      >
        <!-- Topic + meta -->
        <div class="flex flex-wrap items-baseline gap-3 mb-4">
          <span class="num-chapter text-[10px]">{{ String(i + 1).padStart(2, '0') }}</span>
          <h3 class="font-display italic text-xl text-ink-900 flex-1 min-w-0 leading-snug">
            {{ bridge.topic }}
          </h3>
          <span class="font-mono text-[11px] tracking-widest" :class="anchorColor(bridge.anchor_id)">
            ▲ {{ bridge.anchor_id }}
          </span>
          <span class="font-mono text-[11px] text-ink-500 tracking-wider">
            / {{ bridge.category }}
          </span>
        </div>

        <!-- Bridge Sentence —— 大引号 -->
        <blockquote class="relative pl-10 mb-4">
          <span class="absolute left-0 top-0 font-display italic text-5xl text-ochre-500 leading-none select-none">"</span>
          <p class="font-serif italic text-[16px] leading-[1.8] text-ink-700">
            {{ bridge.bridge_sentence }}
          </p>
        </blockquote>

        <!-- Key Phrases -->
        <div class="flex flex-wrap gap-x-5 gap-y-1 mb-4">
          <span
            v-for="(phrase, j) in bridge.key_phrases"
            :key="j"
            class="font-mono text-[12px] text-sage-500 tracking-wide"
          >
            {{ phrase }}
          </span>
        </div>

        <!-- Expandable Sample Answer -->
        <div>
          <button
            @click="toggleExpand(i)"
            class="inline-flex items-center gap-2 font-serif italic text-[13px] text-ink-500 hover:text-ink-900 transition-colors"
          >
            <span class="font-mono text-[10px] text-ochre-500 tracking-widest not-italic">
              {{ expandedItems[i] ? '—' : '+' }}
            </span>
            {{ expandedItems[i] ? 'Hide' : 'Show' }} Sample Answer
          </button>
          <transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-[500px]"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 max-h-[500px]"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="expandedItems[i]" class="mt-4 overflow-hidden">
              <div class="hairline mb-3"></div>
              <p class="font-serif text-[15px] leading-[1.85] text-ink-700">
                {{ bridge.sample_answer }}
              </p>
            </div>
          </transition>
        </div>
      </article>
    </div>

    <p v-if="filteredBridges.length === 0" class="font-serif italic text-ink-500 text-center py-10">
      No bridges catalogued under this heading.
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

const anchorColor = (id) => {
  const colors = {
    A: 'text-indigo-800',
    B: 'text-ochre-500',
    C: 'text-sage-500',
    D: 'text-rouge-600'
  }
  return colors[id] || 'text-ink-500'
}
</script>

<style scoped>
.tab-link {
  position: relative;
  padding-bottom: 0.35rem;
}
.tab-link::after {
  content: '';
  position: absolute;
  left: 0; right: 100%;
  bottom: 0;
  height: 2px;
  background: var(--ochre-500, #C3822F);
  transition: right .25s cubic-bezier(.2,.8,.2,1);
}
.tab-link.is-active::after {
  right: 40%;
}
</style>
