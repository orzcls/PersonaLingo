<template>
  <section id="vocabulary" class="mb-16 stagger">
    <header class="mb-7 flex items-end justify-between flex-wrap gap-4">
      <div>
        <p class="num-chapter text-[11px] mb-2">§ 03 · lexicon</p>
        <h2 class="font-display italic text-3xl md:text-4xl text-ink-900 leading-tight">
          Vocabulary Upgrade
        </h2>
        <p class="mt-2 font-serif text-sm text-ink-500 italic max-w-xl">
          Substitute the plain word with its cultivated cousin.
        </p>
      </div>

      <!-- View Toggle -->
      <div class="flex items-center gap-0 border border-ink-900/15">
        <button
          @click="viewMode = 'card'"
          class="px-3 py-1.5 font-mono text-[10px] tracking-widest transition-colors"
          :class="viewMode === 'card' ? 'bg-ink-900 text-paper-50' : 'text-ink-500 hover:text-ink-900'"
        >CARD</button>
        <button
          @click="viewMode = 'table'"
          class="px-3 py-1.5 font-mono text-[10px] tracking-widest transition-colors border-l border-ink-900/15"
          :class="viewMode === 'table' ? 'bg-ink-900 text-paper-50' : 'text-ink-500 hover:text-ink-900'"
        >TABLE</button>
      </div>
    </header>
    <div class="hairline mb-7"></div>

    <!-- Card View -->
    <div v-if="viewMode === 'card'">
      <div v-for="(group, category) in groupedVocab" :key="category" class="mb-10">
        <div class="flex items-center gap-4 mb-4">
          <span class="font-mono text-ochre-500 text-[10px] tracking-widest">—</span>
          <h3 class="font-display italic text-xl text-ink-900">{{ category }}</h3>
          <span class="hairline flex-1"></span>
          <span class="font-mono text-ink-500 text-[10px] tracking-widest">
            {{ String(group.length).padStart(2, '0') }}
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <article
            v-for="(item, i) in group"
            :key="i"
            class="paper-card p-5"
          >
            <!-- Word upgrade arrow -->
            <div class="flex items-baseline gap-3 mb-3 flex-wrap">
              <span class="font-serif text-ink-500 line-through text-[15px] italic">
                {{ item.basic_word }}
              </span>
              <span class="font-display text-ochre-500 text-xl leading-none">→</span>
              <div class="flex flex-wrap gap-x-3 gap-y-1">
                <span
                  v-for="(alt, j) in item.advanced_alternatives"
                  :key="j"
                  class="font-display italic text-indigo-800 text-[17px] font-medium"
                >
                  {{ alt }}<span v-if="j !== item.advanced_alternatives.length - 1" class="text-ink-300 font-sans">,</span>
                </span>
              </div>
            </div>

            <!-- Example sentence -->
            <p class="font-serif italic text-[14px] leading-[1.75] text-ink-700" v-html="highlightExample(item)"></p>

            <!-- Anchor context -->
            <div class="mt-3 pt-3 border-t border-ink-900/10 flex items-center gap-2">
              <span class="font-mono text-[10px] text-ink-500 tracking-widest">anchor</span>
              <span class="font-mono text-[11px] tracking-widest" :class="anchorColor(item.anchor_context)">
                ▲ {{ item.anchor_context }}
              </span>
            </div>
          </article>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-else class="overflow-x-auto paper-card">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-ink-900/20">
            <th class="text-left py-3 px-5 field-label">Basic</th>
            <th class="text-left py-3 px-5 field-label">Upgrades</th>
            <th class="text-left py-3 px-5 field-label">Example</th>
            <th class="text-left py-3 px-5 field-label">Category</th>
            <th class="text-left py-3 px-5 field-label">Anchor</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, i) in vocabulary"
            :key="i"
            class="border-b border-ink-900/10 hover:bg-paper-100/50 transition-colors"
          >
            <td class="py-3 px-5 font-serif italic text-ink-500 line-through">{{ item.basic_word }}</td>
            <td class="py-3 px-5">
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(alt, j) in item.advanced_alternatives"
                  :key="j"
                  class="font-display italic text-indigo-800 text-[14px]"
                >
                  {{ alt }}
                </span>
              </div>
            </td>
            <td class="py-3 px-5 font-serif text-ink-700 max-w-xs truncate">{{ item.example_sentence }}</td>
            <td class="py-3 px-5 font-mono text-[11px] text-ink-500 tracking-wider">{{ item.category }}</td>
            <td class="py-3 px-5">
              <span class="font-mono text-[11px] tracking-widest" :class="anchorColor(item.anchor_context)">
                ▲ {{ item.anchor_context }}
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
  item.advanced_alternatives.forEach(word => {
    const regex = new RegExp(`(${word})`, 'gi')
    sentence = sentence.replace(regex, '<span style="color:#1E3A8A;font-style:normal;font-weight:500;border-bottom:1px solid #C3822F">$1</span>')
  })
  return sentence
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
