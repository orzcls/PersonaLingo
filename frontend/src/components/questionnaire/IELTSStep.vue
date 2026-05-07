<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h2 class="text-2xl font-bold text-white mb-2">IELTS Speaking Preferences</h2>
      <p class="text-dark-400">Customize your corpus for your IELTS speaking goals</p>
    </div>

    <!-- Topic Types -->
    <div class="space-y-4">
      <h3 class="text-white font-semibold">Preferred Topic Types</h3>
      <p class="text-dark-500 text-sm">Select the types of topics you want to focus on</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        <button
          v-for="topic in topicTypes"
          :key="topic.id"
          :class="[
            'flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200',
            selectedTopics.includes(topic.id)
              ? 'border-accent-400 bg-accent-400/10 text-accent-300'
              : 'border-dark-700 bg-dark-800 text-dark-400 hover:border-dark-500 hover:text-white'
          ]"
          @click="toggleTopic(topic.id)"
        >
          <span class="text-2xl">{{ topic.icon }}</span>
          <span class="text-sm font-medium">{{ topic.label }}</span>
        </button>
      </div>
    </div>

    <!-- Divider -->
    <div class="border-t border-dark-700" />

    <!-- Target Band Score -->
    <div class="space-y-4">
      <h3 class="text-white font-semibold">Target Band Score</h3>
      <p class="text-dark-500 text-sm">Choose your target score to adjust difficulty and vocabulary level</p>
      <div class="flex gap-3">
        <button
          v-for="band in bandOptions"
          :key="band"
          :class="[
            'flex-1 py-3 px-4 rounded-xl border-2 text-center font-bold transition-all duration-200',
            selectedBand === band
              ? 'border-accent-400 bg-accent-400/10 text-accent-400 shadow-lg shadow-accent-500/10'
              : 'border-dark-700 bg-dark-800 text-dark-300 hover:border-dark-500 hover:text-white'
          ]"
          @click="selectBand(band)"
        >
          {{ band }}
        </button>
      </div>
      <div v-if="selectedBand" class="bg-dark-800 rounded-lg px-4 py-3 border border-dark-700">
        <p class="text-dark-300 text-sm">{{ bandDescriptions[selectedBand] }}</p>
      </div>
    </div>

    <!-- Divider -->
    <div class="border-t border-dark-700" />

    <!-- Exam Month -->
    <div class="space-y-4">
      <h3 class="text-white font-semibold">Exam Timeline</h3>
      <p class="text-dark-500 text-sm">When are you planning to take the exam?</p>
      <div class="grid grid-cols-3 gap-3">
        <button
          v-for="month in examMonths"
          :key="month.value"
          :class="[
            'py-3 px-4 rounded-xl border-2 text-center transition-all duration-200',
            selectedMonth === month.value
              ? 'border-accent-400 bg-accent-400/10 text-accent-400'
              : 'border-dark-700 bg-dark-800 text-dark-300 hover:border-dark-500 hover:text-white'
          ]"
          @click="selectMonth(month.value)"
        >
          <span class="block font-semibold text-sm">{{ month.label }}</span>
          <span class="block text-xs mt-0.5 opacity-70">{{ month.year }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()

const topicTypes = [
  { id: 'people', label: 'People', icon: '👤' },
  { id: 'places', label: 'Places', icon: '🌍' },
  { id: 'events', label: 'Events', icon: '🎉' },
  { id: 'objects', label: 'Objects', icon: '📦' },
  { id: 'abstract', label: 'Abstract', icon: '💭' },
]

const bandOptions = ['6.0', '6.5', '7.0', '7.5+']

const bandDescriptions = {
  '6.0': 'Competent user — generally effective command of the language with some inaccuracies and misunderstandings.',
  '6.5': 'Between competent and good — can handle complex language well with occasional errors.',
  '7.0': 'Good user — operational command of the language with occasional inaccuracies.',
  '7.5+': 'Very good user — fluent with only rare errors, handles complex language well.',
}

// Generate exam months (current + next 2 months)
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
  if (idx > -1) {
    selectedTopics.value.splice(idx, 1)
  } else {
    selectedTopics.value.push(id)
  }
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
