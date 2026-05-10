<template>
  <div class="space-y-10">
    <!-- Header -->
    <header class="text-center space-y-3">
      <p class="num-chapter">§ 04 · IELTS Speaking</p>
      <h2 class="font-display text-3xl text-ink-900" style="font-variation-settings:'opsz' 96, 'SOFT' 50;">
        备考 <em class="italic text-ochre-500">偏好</em>
      </h2>
      <p class="text-ink-500 font-serif italic">Customise your corpus for your IELTS speaking goals.</p>
    </header>

    <!-- Topic Types -->
    <section class="space-y-4">
      <h3 class="rule-heading font-serif italic text-ink-700 text-sm">
        <span class="px-4">Preferred topic types</span>
      </h3>
      <p class="text-ink-500 text-sm font-serif italic text-center">Select the types of topics you want to focus on.</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        <button
          v-for="(topic, idx) in topicTypes"
          :key="topic.id"
          :class="[
            'group flex flex-col items-center gap-2 p-5 transition-colors duration-300',
            selectedTopics.includes(topic.id)
              ? 'bg-paper-100 hairline-strong text-ink-900'
              : 'hairline text-ink-500 hover:text-ink-900'
          ]"
          @click="toggleTopic(topic.id)"
        >
          <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
            {{ String(idx + 1).padStart(2, '0') }}
          </span>
          <span class="font-serif text-base">{{ topic.label }}</span>
        </button>
      </div>
    </section>

    <div class="hairline-t"></div>

    <!-- Target Band Score -->
    <section class="space-y-4">
      <h3 class="rule-heading font-serif italic text-ink-700 text-sm">
        <span class="px-4">Target band score</span>
      </h3>
      <p class="text-ink-500 text-sm font-serif italic text-center">
        Choose your target score to adjust difficulty and vocabulary level.
      </p>
      <div class="grid grid-cols-4 gap-3">
        <button
          v-for="band in bandOptions"
          :key="band"
          :class="[
            'py-4 text-center transition-colors duration-300',
            selectedBand === band
              ? 'chip-ink-selected'
              : 'hairline text-ink-700 hover:text-ink-900'
          ]"
          @click="selectBand(band)"
        >
          <span class="font-display text-xl" style="font-variation-settings:'opsz' 144, 'SOFT' 40;">{{ band }}</span>
        </button>
      </div>
      <div v-if="selectedBand" class="paper-card-muted px-5 py-4">
        <p class="text-ink-700 text-sm font-serif leading-relaxed">
          <span class="font-display italic text-ochre-500 mr-1">”</span>{{ bandDescriptions[selectedBand] }}
        </p>
      </div>
    </section>

    <div class="hairline-t"></div>

    <!-- Exam Month -->
    <section class="space-y-4">
      <h3 class="rule-heading font-serif italic text-ink-700 text-sm">
        <span class="px-4">Exam timeline</span>
      </h3>
      <p class="text-ink-500 text-sm font-serif italic text-center">When are you planning to take the exam?</p>
      <div class="grid grid-cols-3 gap-3">
        <button
          v-for="month in examMonths"
          :key="month.value"
          :class="[
            'py-4 text-center transition-colors duration-300',
            selectedMonth === month.value
              ? 'bg-paper-100 hairline-strong text-ink-900'
              : 'hairline text-ink-500 hover:text-ink-900'
          ]"
          @click="selectMonth(month.value)"
        >
          <span class="block font-display text-lg italic">{{ month.label }}</span>
          <span class="block font-mono text-xs tracking-[0.22em] text-ochre-500 mt-0.5">{{ month.year }}</span>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()

const topicTypes = [
  { id: 'people', label: 'People' },
  { id: 'places', label: 'Places' },
  { id: 'events', label: 'Events' },
  { id: 'objects', label: 'Objects' },
  { id: 'abstract', label: 'Abstract' },
]

const bandOptions = ['6.0', '6.5', '7.0', '7.5+']

const bandDescriptions = {
  '6.0': 'Competent user — generally effective command of the language with some inaccuracies and misunderstandings.',
  '6.5': 'Between competent and good — can handle complex language well with occasional errors.',
  '7.0': 'Good user — operational command of the language with occasional inaccuracies.',
  '7.5+': 'Very good user — fluent with only rare errors, handles complex language well.',
}

const examMonths = computed(() => {
  const months = []
  const now = new Date()
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  for (let i = 0; i < 3; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1)
    months.push({
      value: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      label: monthNames[d.getMonth()],
      year: d.getFullYear()
    })
  }
  return months
})

const selectedTopics = ref([...store.ieltsPreference.topicTypes])
const selectedBand = ref(store.ieltsPreference.targetBand)
const selectedMonth = ref(store.ieltsPreference.examMonth)

function toggleTopic(id) {
  const idx = selectedTopics.value.indexOf(id)
  if (idx > -1) selectedTopics.value.splice(idx, 1)
  else selectedTopics.value.push(id)
  store.setIELTSPreference({ topicTypes: [...selectedTopics.value] })
}

function selectBand(band) {
  selectedBand.value = band
  store.setIELTSPreference({ targetBand: band })
}

function selectMonth(month) {
  selectedMonth.value = month
  store.setIELTSPreference({ examMonth: month })
}
</script>
