<template>
  <div class="flex flex-col items-center justify-center gap-6 py-12">
    <!-- Three ink droplets diffusing across paper -->
    <div class="relative w-28 h-10 flex items-center justify-center" aria-hidden="true">
      <span
        v-for="i in 3"
        :key="i"
        class="ink-dot"
        :style="{ animationDelay: `${(i - 1) * 0.22}s`, left: `${(i - 1) * 28}px` }"
      />
    </div>

    <p v-if="message" class="font-serif italic text-ink-500 text-base tracking-wide">
      {{ message }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  message: { type: String, default: '' }
})
</script>

<style scoped>
.ink-dot {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #2C3E6B, #0F1220 80%);
  opacity: .55;
  transform-origin: center;
  animation: ink-diffuse 1.8s cubic-bezier(.2, .8, .2, 1) infinite;
}

@keyframes ink-diffuse {
  0%   { transform: scale(.55);  opacity: .15; filter: blur(0);   }
  45%  { transform: scale(1.05); opacity: .85; filter: blur(.3px); }
  100% { transform: scale(2.0);  opacity: 0;   filter: blur(1px);  }
}

@media (prefers-reduced-motion: reduce) {
  .ink-dot { animation: none; opacity: .6; }
}
</style>
