<template>
  <div class="flex flex-col items-center justify-center space-y-6 py-12">
    <!-- Spinner Animation -->
    <div class="relative">
      <div class="w-16 h-16 border-4 border-dark-700 rounded-full"></div>
      <div class="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-accent-400 rounded-full animate-spin"></div>
      <!-- Pulse ring -->
      <div class="absolute -inset-2 border-2 border-accent-400/20 rounded-full animate-pulse"></div>
    </div>

    <!-- Message -->
    <p v-if="message" class="text-dark-300 text-lg font-medium animate-pulse">
      {{ message }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  }
})
</script>
