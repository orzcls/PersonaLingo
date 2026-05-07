<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h2 class="text-2xl font-bold text-white mb-2">Your Interests & Hobbies</h2>
      <p class="text-dark-400">Select topics you enjoy and describe your hobbies in detail</p>
    </div>

    <!-- Interest Tag Cloud -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-white font-semibold">Interest Tags</h3>
        <span :class="[
          'text-sm font-medium',
          selectedTags.length < 3 ? 'text-amber-400' : selectedTags.length > 8 ? 'text-red-400' : 'text-accent-400'
        ]">
          {{ selectedTags.length }}/8 selected
          <span v-if="selectedTags.length < 3" class="text-dark-400 ml-1">(min 3)</span>
        </span>
      </div>
      <div class="flex flex-wrap gap-2.5">
        <button
          v-for="tag in availableTags"
          :key="tag"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium border transition-all duration-200',
            selectedTags.includes(tag)
              ? 'border-accent-400 bg-accent-400/15 text-accent-300 shadow-sm shadow-accent-500/10'
              : 'border-dark-600 bg-dark-800 text-dark-300 hover:border-dark-400 hover:text-white'
          ]"
          :disabled="!selectedTags.includes(tag) && selectedTags.length >= 8"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>

    <!-- Divider -->
    <div class="border-t border-dark-700" />

    <!-- Hobby Descriptions -->
    <div class="space-y-5">
      <div class="flex items-center justify-between">
        <h3 class="text-white font-semibold">Describe your top 3 hobbies/experiences in detail</h3>
        <span class="text-dark-500 text-xs">Recommended 50-150 words each</span>
      </div>

      <div v-for="(desc, index) in descriptions" :key="index" class="space-y-2">
        <label class="flex items-center gap-2 text-sm text-dark-300">
          <span class="w-6 h-6 rounded-full bg-dark-700 flex items-center justify-center text-xs font-bold text-accent-400">
            {{ index + 1 }}
          </span>
          Hobby {{ index + 1 }}
        </label>
        <div class="relative">
          <textarea
            :value="descriptions[index]"
            @input="updateDescription(index, $event.target.value)"
            :placeholder="placeholders[index]"
            rows="4"
            class="w-full bg-dark-800 border border-dark-700 rounded-xl px-4 py-3 text-white placeholder-dark-500 text-sm resize-none focus:outline-none focus:border-accent-500 focus:ring-1 focus:ring-accent-500/30 transition-all duration-200"
          />
          <span :class="[
            'absolute bottom-3 right-3 text-xs',
            wordCount(descriptions[index]) > 150 ? 'text-amber-400' : wordCount(descriptions[index]) >= 50 ? 'text-accent-400' : 'text-dark-500'
          ]">
            {{ wordCount(descriptions[index]) }} words
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()

const availableTags = [
  'Photography', 'Music', 'Coding', 'Gaming', 'Reading',
  'Travel', 'Sports', 'Cooking', 'Art', 'Film',
  'Nature', 'Writing', 'Dance', 'Fitness', 'Technology',
  'Science', 'History', 'Philosophy', 'Fashion', 'Animals'
]

const placeholders = [
  'Describe your first hobby — what you do, why you love it, a memorable moment...',
  'Describe your second hobby — how you got into it, what excites you about it...',
  'Describe your third hobby — how often you do it, who you share it with...'
]

const selectedTags = ref([...store.interests.tags])
const descriptions = ref([...store.interests.descriptions])

function toggleTag(tag) {
  const idx = selectedTags.value.indexOf(tag)
  if (idx > -1) {
    selectedTags.value.splice(idx, 1)
  } else if (selectedTags.value.length < 8) {
    selectedTags.value.push(tag)
  }
  store.setInterestTags([...selectedTags.value])
}

function updateDescription(index, value) {
  descriptions.value[index] = value
  store.setInterestDescription(index, value)
}

function wordCount(text) {
  if (!text || !text.trim()) return 0
  return text.trim().split(/\s+/).length
}

// Sync from store if navigating back
watch(() => store.interests.tags, (val) => {
  selectedTags.value = [...val]
}, { deep: true })
</script>
