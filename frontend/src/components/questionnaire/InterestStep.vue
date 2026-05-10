<template>
  <div class="space-y-10">
    <!-- Header -->
    <header class="text-center space-y-3">
      <p class="num-chapter">§ 03 · Interests</p>
      <h2 class="font-display text-3xl text-ink-900" style="font-variation-settings:'opsz' 96, 'SOFT' 50;">
        兴趣 <em class="italic text-ochre-500">爱好</em>
      </h2>
      <p class="text-ink-500 font-serif italic">选择最能代表你的兴趣标签 · 也可自定义添加</p>
    </header>

    <!-- Selected Tags Display -->
    <section v-if="selectedTags.length > 0" class="space-y-3">
      <div class="flex items-baseline justify-between">
        <h3 class="field-label">已选标签</h3>
        <span class="font-mono text-xs tracking-[0.22em]"
          :class="selectedTags.length < 3 ? 'text-rouge-600' : 'text-sage-500'">
          {{ String(selectedTags.length).padStart(2, '0') }} SELECTED
          <span v-if="selectedTags.length < 3" class="text-ink-500 ml-1 normal-case tracking-normal font-serif italic normal-case">(建议 ≥ 3)</span>
        </span>
      </div>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="(tag, index) in selectedTags"
          :key="'selected-' + index"
          class="inline-flex items-center px-3 py-1 text-sm font-serif transition-colors duration-300 hairline"
          :class="tag.isCustom ? 'bg-sage-500/10 text-sage-500' : 'bg-ochre-300/25 text-ochre-500'"
        >
          {{ tag.name }}
          <button @click="removeTag(index)" class="ml-2 text-ink-500 hover:text-ink-900 transition-colors">×</button>
        </span>
      </div>
    </section>

    <!-- Custom Tag Input -->
    <section class="space-y-2">
      <label class="field-label">Custom tag</label>
      <div class="relative">
        <input
          v-model="customInput"
          @keydown.enter.prevent="addCustomTag"
          placeholder="输入自定义兴趣标签，回车添加⋯"
          class="input-hairline pr-16"
        />
        <span class="absolute right-3 top-1/2 -translate-y-1/2 font-mono text-[10px] tracking-[0.22em] text-ink-500">Enter ↵</span>
      </div>
    </section>

    <div class="hairline-t"></div>

    <!-- Interest Tag Cloud by Category -->
    <section class="space-y-7">
      <div class="text-center space-y-1">
        <h3 class="rule-heading font-serif italic text-ink-700 text-sm">
          <span class="px-4">Preset tags</span>
        </h3>
        <p class="text-ink-500 text-xs font-serif italic">选择 3–10 个最能代表你的标签</p>
      </div>

      <div v-for="(category, cIdx) in tagCategories" :key="category.name" class="space-y-3">
        <h4 class="flex items-baseline gap-3">
          <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
            {{ String(cIdx + 1).padStart(2, '0') }}
          </span>
          <span class="font-display italic text-ink-700">{{ category.name }}</span>
          <span class="flex-1 h-px bg-ink-900/10 self-center"></span>
        </h4>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in category.tags"
            :key="tag"
            :class="[
              'px-3.5 py-1.5 text-sm font-serif transition-colors duration-300',
              isPresetSelected(tag)
                ? 'bg-ochre-300/30 text-ink-900 hairline-strong'
                : 'hairline text-ink-500 hover:text-ink-900'
            ]"
            @click="togglePresetTag(tag)"
          >
            {{ tag }}
          </button>
        </div>
      </div>
    </section>

    <div class="hairline-t"></div>

    <!-- Hobby Descriptions -->
    <section class="space-y-5">
      <div class="flex items-baseline justify-between">
        <h3 class="field-label">Describe your hobbies <span class="text-ink-500 normal-case tracking-normal font-serif italic">(optional)</span></h3>
        <span class="font-mono text-[10px] tracking-[0.22em] text-ink-500">≈ 50–150 WORDS</span>
      </div>

      <div v-for="(desc, index) in descriptions" :key="index" class="space-y-2">
        <label class="flex items-center gap-3 text-sm">
          <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
            {{ String(index + 1).padStart(2, '0') }}
          </span>
          <span class="font-display italic text-ink-700">Hobby {{ index + 1 }}</span>
        </label>
        <div class="relative">
          <textarea
            :value="descriptions[index]"
            @input="updateDescription(index, $event.target.value)"
            :placeholder="placeholders[index]"
            rows="4"
            class="input-hairline resize-none font-serif"
          />
          <span class="absolute bottom-3 right-3 font-mono text-[10px] tracking-[0.22em]"
            :class="wordCount(descriptions[index]) > 150 ? 'text-rouge-600' : wordCount(descriptions[index]) >= 50 ? 'text-sage-500' : 'text-ink-500'">
            {{ wordCount(descriptions[index]) }} W
          </span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()

const tagCategories = [
  { name: 'Creative', tags: ['Photography', 'Music', 'Art', 'Writing', 'Film', 'Dance'] },
  { name: 'Tech', tags: ['Coding', 'AIGC', 'Gaming', 'Technology', 'Science'] },
  { name: 'Lifestyle', tags: ['Travel', 'Cooking', 'Reading', 'Fitness', 'Fashion'] },
  { name: 'Nature', tags: ['Nature', 'Animals', 'Gardening', 'Hiking', 'Stargazing'] },
  { name: 'Social', tags: ['Volunteering', 'Sports', 'Board Games', 'Table Tennis', 'Piano'] }
]

const placeholders = [
  'Describe your first hobby — what you do, why you love it, a memorable moment⋯',
  'Describe your second hobby — how you got into it, what excites you about it⋯',
  'Describe your third hobby — how often you do it, who you share it with⋯'
]

function initTags() {
  const storeTags = store.interests.tags
  if (storeTags.length === 0) return []
  if (typeof storeTags[0] === 'string') {
    return storeTags.map(t => ({ name: t, isCustom: false }))
  }
  return [...storeTags]
}

const selectedTags = ref(initTags())
const customInput = ref(store.interests.customInput || '')
const descriptions = ref([...store.interests.descriptions])

function isPresetSelected(tagName) {
  return selectedTags.value.some(t => t.name === tagName && !t.isCustom)
}

function togglePresetTag(tagName) {
  const idx = selectedTags.value.findIndex(t => t.name === tagName && !t.isCustom)
  if (idx > -1) selectedTags.value.splice(idx, 1)
  else selectedTags.value.push({ name: tagName, isCustom: false })
  syncToStore()
}

function addCustomTag() {
  const val = customInput.value.trim()
  if (!val) return
  if (selectedTags.value.some(t => t.name.toLowerCase() === val.toLowerCase())) {
    customInput.value = ''
    return
  }
  selectedTags.value.push({ name: val, isCustom: true })
  customInput.value = ''
  syncToStore()
}

function removeTag(index) {
  selectedTags.value.splice(index, 1)
  syncToStore()
}

function syncToStore() {
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

watch(() => store.interests.tags, (val) => {
  if (val.length === 0) {
    selectedTags.value = []
  } else if (typeof val[0] === 'string') {
    selectedTags.value = val.map(t => ({ name: t, isCustom: false }))
  } else {
    selectedTags.value = [...val]
  }
}, { deep: true })
</script>