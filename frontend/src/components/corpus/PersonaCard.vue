<template>
  <section class="mb-10">
    <article class="paper-card relative p-7 md:p-10 overflow-hidden">
      <!-- 角标：章节序号 -->
      <div class="absolute top-5 right-6 text-right">
        <p class="num-chapter text-[10px]">fol. 001</p>
        <p class="font-mono text-[10px] text-ink-500 tracking-widest mt-0.5">DOSSIER</p>
      </div>

      <!-- Top：MBTI 印章 + 名称 -->
      <div class="flex flex-wrap items-end gap-6 mb-7">
        <div class="flex items-center gap-5">
          <div class="shrink-0 w-20 h-20 border border-ink-900/70 flex items-center justify-center bg-paper-50 relative">
            <span class="font-display italic font-semibold text-ink-900 text-2xl tracking-tight">{{ persona.mbti_type }}</span>
            <span class="absolute -bottom-2 left-1/2 -translate-x-1/2 px-2 bg-paper-50 font-mono text-[9px] text-ochre-500 tracking-widest">TYPE</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="num-chapter text-[11px] mb-1">§ persona</p>
            <h2 class="font-display italic text-3xl md:text-4xl text-ink-900 leading-none tracking-tight">
              {{ persona.mbti_type }}
            </h2>
            <p class="mt-2 font-serif text-sm text-ink-500 italic">{{ persona.mbti_description }}</p>
          </div>
        </div>
        <div class="ml-auto flex flex-col items-end gap-2 text-right">
          <div>
            <p class="num-chapter text-[10px] mb-0.5">target band</p>
            <p class="font-display text-3xl text-ochre-500 leading-none">{{ persona.target_score }}</p>
          </div>
          <p v-if="persona.exam_date" class="font-mono text-[11px] text-ink-500 tracking-wider">
            exam · {{ persona.exam_date }}
          </p>
        </div>
      </div>

      <div class="hairline w-full my-6"></div>

      <!-- Communication Style —— 诗化段落，首字下沉 -->
      <div class="mb-7 grid md:grid-cols-[120px,1fr] gap-4 md:gap-8">
        <p class="field-label md:text-right pt-1">Voice</p>
        <p class="font-serif text-[15px] leading-[1.9] text-ink-700 drop-cap">
          {{ persona.communication_style }}
        </p>
      </div>

      <!-- Interests -->
      <div class="mb-6 grid md:grid-cols-[120px,1fr] gap-4 md:gap-8">
        <p class="field-label md:text-right pt-1">Interests</p>
        <div class="flex flex-wrap gap-x-5 gap-y-2">
          <span
            v-for="(tag, i) in persona.interest_tags"
            :key="i"
            class="font-serif italic text-ink-700 text-[15px] relative"
          >
            <span class="font-mono text-ochre-500 text-[10px] tracking-widest mr-1.5 align-middle">{{ String(i + 1).padStart(2, '0') }}</span>{{ tag }}
          </span>
        </div>
      </div>

      <!-- Topic Focus -->
      <div v-if="persona.topic_focus && persona.topic_focus.length" class="grid md:grid-cols-[120px,1fr] gap-4 md:gap-8">
        <p class="field-label md:text-right pt-1">Focus</p>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(topic, i) in persona.topic_focus"
            :key="i"
            class="px-3 py-1 border border-ink-900/15 text-ink-700 font-serif text-xs tracking-wide"
          >
            {{ topic }}
          </span>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup>
defineProps({
  persona: {
    type: Object,
    required: true
  }
})
</script>
