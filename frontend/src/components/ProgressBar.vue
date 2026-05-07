<template>
  <div class="w-full">
    <div class="flex items-center justify-between">
      <template v-for="(step, index) in steps" :key="index">
        <!-- Step circle -->
        <div class="flex flex-col items-center relative">
          <div
            :class="[
              'w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300',
              index + 1 <= currentStep
                ? 'bg-accent-500 text-white shadow-lg shadow-accent-500/30'
                : 'bg-dark-700 text-dark-400'
            ]"
          >
            <span v-if="index + 1 < currentStep">✓</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span
            :class="[
              'mt-2 text-xs font-medium whitespace-nowrap',
              index + 1 <= currentStep ? 'text-accent-400' : 'text-dark-500'
            ]"
          >
            {{ step }}
          </span>
        </div>

        <!-- Connector line -->
        <div
          v-if="index < steps.length - 1"
          :class="[
            'flex-1 h-0.5 mx-3 transition-all duration-300',
            index + 1 < currentStep ? 'bg-accent-500' : 'bg-dark-700'
          ]"
        />
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  steps: {
    type: Array,
    required: true
  },
  currentStep: {
    type: Number,
    required: true
  }
})
</script>
