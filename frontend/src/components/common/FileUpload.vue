<template>
  <div
    class="relative p-8 text-center cursor-pointer transition-all duration-300"
    :class="[
      'hairline',
      isDragging
        ? 'bg-paper-100 border-ink-900'
        : 'hover:bg-paper-100/50 hover:border-ink-300/40'
    ]"
    style="border-style: dashed;"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
    @click="triggerFileInput"
  >
    <input
      ref="fileInput"
      type="file"
      class="hidden"
      :accept="acceptTypes"
      @change="handleFileChange"
    />

    <div class="flex flex-col items-center gap-4">
      <svg class="w-10 h-10 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3">
        <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 11v10m0-10l-3 3m3-3l3 3" />
      </svg>

      <div>
        <p class="font-serif text-lg text-ink-900 mb-1">
          {{ isDragging ? 'Release to upload' : 'Drop a file here, or click to browse' }}
        </p>
        <p class="field-label">Supports .txt · .md · .docx · .pdf</p>
      </div>

      <div v-if="selectedFile" class="mt-1 px-4 py-2 paper-card-muted">
        <p class="font-mono text-sm text-indigo-800">{{ selectedFile.name }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])

const fileInput = ref(null)
const isDragging = ref(false)
const selectedFile = ref(null)

const acceptTypes = '.txt,.md,.docx,.pdf'

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    emit('file-selected', file)
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
    emit('file-selected', file)
  }
}
</script>
