<template>
  <div class="w-full">
    <!-- Tick ruler -->
    <div class="relative flex items-end gap-0 h-10">
      <template v-for="(step, index) in steps" :key="index">
        <div class="flex-1 flex flex-col items-start">
          <span
            class="font-mono text-[0.62rem] tracking-[0.22em] uppercase tabular-nums"
            :class="index + 1 <= currentStep ? 'text-ochre-500' : 'text-ink-300'"
          >
            {{ String(index + 1).padStart(2, '0') }}
          </span>
          <span
            class="block mt-1 h-3 w-px"
            :class="index + 1 <= currentStep ? 'bg-indigo-800' : 'bg-ink-300/60'"
          />
          <span
            class="mt-2 font-serif text-xs tracking-wide whitespace-nowrap"
            :class="index + 1 <= currentStep ? 'text-ink-900' : 'text-ink-500'"
          >
            {{ step }}
          </span>
        </div>
      </template>
    </div>

    <!-- Ruler baseline with ink fill -->
    <div class="relative mt-1 h-px bg-ink-200/60">
      <div
        class="absolute inset-y-0 left-0 bg-indigo-800 transition-[width] duration-500"
        :style="{ width: progressPct + '%' }"
      />
    </div>

    <!-- Numeric read-out -->
    <div class="flex items-baseline justify-between mt-3">
      <span class="font-mono text-[0.66rem] tracking-[0.22em] uppercase text-ink-500">
        Progress
      </span>
      <span class="font-mono text-sm tabular-nums text-ink-900">
        {{ String(Math.min(currentStep, steps.length)).padStart(2, '0') }}
        <span class="text-ink-300"> / {{ String(steps.length).padStart(2, '0') }}</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: { type: Array, required: true },
  currentStep: { type: Number, required: true }
})

const progressPct = computed(() => {
  if (!props.steps.length) return 0
  return Math.max(0, Math.min(100, ((props.currentStep - 0.5) / props.steps.length) * 100))
})
</script>
