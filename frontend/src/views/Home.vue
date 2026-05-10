<template>
  <div class="bg-paper-50">
    <!-- =================== Hero =================== -->
    <section class="relative overflow-hidden">
      <!-- Side decorative chapter marker -->
      <div class="pointer-events-none absolute top-10 right-6 md:right-10 select-none">
        <span class="block font-mono text-[0.68rem] tracking-[0.28em] text-ochre-500">CHAPTER</span>
        <span class="block font-display italic text-5xl md:text-7xl leading-none text-ink-900/90 mt-1"
              style="font-variation-settings: 'opsz' 144, 'SOFT' 60;">I</span>
      </div>

      <div class="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12 pt-16 pb-20 lg:pt-24 lg:pb-28">
        <div class="grid lg:grid-cols-12 gap-10 lg:gap-16 items-end">
          <!-- Left column — title / subtitle / CTA -->
          <div class="lg:col-span-7 stagger">
            <p class="field-label mb-6">An AI-tuned field notebook &middot; est. 2026</p>

            <h1 class="font-display text-ink-900 leading-[0.92] tracking-[-0.02em]"
                style="font-variation-settings: 'opsz' 144, 'SOFT' 30;">
              <span class="block text-[3.2rem] md:text-[5.2rem] lg:text-[6rem]">Persona</span>
              <span class="block text-[3.2rem] md:text-[5.2rem] lg:text-[6rem] italic text-indigo-800">
                Lingo<span class="text-ochre-500 align-super text-[0.45em] ml-1">&lowast;01</span>
              </span>
            </h1>

            <!-- Divider flourish -->
            <div class="mt-8 flex items-center gap-4">
              <span class="block h-px w-12 bg-ink-900/40"></span>
              <span class="font-mono text-[0.68rem] tracking-[0.28em] text-ink-500 uppercase">
                A quiet workshop for your spoken voice
              </span>
            </div>

            <p class="mt-6 font-serif text-xl lg:text-[1.35rem] text-ink-700 max-w-2xl leading-relaxed">
              {{ t('home.subtitle') }}
            </p>

            <p class="mt-4 font-serif italic text-ink-500 max-w-2xl">
              &ldquo;{{ t('home.slogan') }}&rdquo;
            </p>

            <div class="mt-10 flex flex-wrap items-center gap-5">
              <router-link to="/questionnaire" class="btn-ink">
                <span>{{ t('home.cta') }}</span>
                <svg class="arrow w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" d="M5 12h14m0 0l-6-6m6 6l-6 6" />
                </svg>
              </router-link>

              <router-link to="/topics" class="flex items-baseline gap-2 text-ink-700 hover:text-indigo-800 transition-colors">
                <span class="font-mono text-[0.68rem] tracking-[0.28em] text-ochre-500">02 &rarr;</span>
                <span class="font-serif ink-underline">Browse the topic bank</span>
              </router-link>
            </div>
          </div>

          <!-- Right column — book-page preview card -->
          <div class="lg:col-span-5 stagger">
            <article class="paper-card p-7 md:p-9 relative overflow-hidden">
              <div class="flex items-baseline justify-between mb-5">
                <span class="num-chapter">&sect; 03 &middot; Field note</span>
                <span class="font-mono text-xs tabular-nums text-ink-300">fol. 014</span>
              </div>

              <h3 class="font-display text-2xl md:text-[1.7rem] text-ink-900 leading-snug mb-4"
                  style="font-variation-settings: 'opsz' 48, 'SOFT' 40;">
                On growing up in a small city in Sichuan,
                <span class="italic text-indigo-800">and the slow formation of voice.</span>
              </h3>

              <div class="ruled-lines">
                <p class="drop-cap font-serif text-[0.98rem] text-ink-700 leading-[1.68]">
                  The afternoons were made of bicycle bells and chalk dust &mdash; and, later, of the quiet thrill of
                  finding one&rsquo;s own words in a borrowed language. This notebook holds the anchors, the
                  bridges, the shy little phrases that stitch an answer together.
                </p>
              </div>

              <!-- Footnote -->
              <div class="mt-6 pt-4 hairline-t flex items-baseline justify-between gap-4">
                <span class="font-serif italic text-sm text-ink-500">
                  &mdash; extracted anchor #014, personal
                </span>
                <span class="font-mono text-[0.68rem] tracking-[0.22em] text-ochre-500 uppercase">
                  Corpus / Vol. I
                </span>
              </div>

              <!-- Paper edge ornament -->
              <span class="absolute top-0 right-0 w-16 h-16 pointer-events-none"
                    style="background: linear-gradient(225deg, rgba(232,222,198,0.7) 0%, rgba(232,222,198,0) 60%);"></span>
            </article>

            <p class="mt-4 font-mono text-[0.68rem] tracking-[0.22em] text-ink-500 uppercase text-right">
              A sample page from a learner&apos;s notebook
            </p>
          </div>
        </div>
      </div>

      <!-- Lower hairline rule -->
      <div class="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <div class="hairline-t"></div>
      </div>
    </section>

    <!-- =================== Features / Masthead =================== -->
    <section class="py-20 lg:py-28">
      <div class="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <div class="flex items-end justify-between mb-12 lg:mb-16 flex-wrap gap-4">
          <div>
            <p class="num-chapter mb-3">&sect; 02 &middot; Features</p>
            <h2 class="font-display text-ink-900 text-4xl lg:text-[2.75rem] tracking-tight leading-tight"
                style="font-variation-settings: 'opsz' 96, 'SOFT' 40;">
              {{ t('home.featuresTitle') }},
              <span class="italic text-indigo-800">laid out as a small masthead.</span>
            </h2>
          </div>
          <p class="font-serif italic text-ink-500 max-w-sm">
            Six tools, arranged the way a writer would. Open the one the moment asks for.
          </p>
        </div>

        <!-- Two-column editorial feature grid -->
        <div class="grid md:grid-cols-2 gap-x-16 gap-y-0">
          <article
            v-for="(feat, idx) in features"
            :key="feat.key"
            class="relative py-8 hairline-b last:border-b-0 md:[&:nth-last-child(-n+2)]:border-b-0 group stagger"
          >
            <div class="flex items-start gap-6">
              <span class="font-mono text-[0.72rem] tracking-[0.28em] text-ochre-500 pt-1 w-10 shrink-0 tabular-nums">
                {{ String(idx + 1).padStart(2, '0') }}
              </span>

              <div class="flex-1 min-w-0">
                <div class="flex items-start gap-5">
                  <div class="shrink-0 mt-1 w-10 h-10 hairline flex items-center justify-center rounded-sm text-ink-900 group-hover:text-indigo-800 transition-colors">
                    <component :is="feat.icon" class="w-5 h-5" />
                  </div>
                  <div class="flex-1">
                    <h3 class="font-display text-[1.4rem] text-ink-900 leading-snug mb-2 tracking-tight">
                      <span class="ink-underline">{{ t(`home.features.${feat.key}.title`) }}</span>
                    </h3>
                    <p class="font-serif text-ink-700 leading-relaxed max-w-md">
                      {{ t(`home.features.${feat.key}.desc`) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <!-- Editorial sign-off -->
        <div class="mt-20 flex items-baseline justify-between hairline-t pt-6">
          <p class="font-serif italic text-ink-500 text-sm">
            &mdash; Composed in ink &amp; silence, reviewed by you alone.
          </p>
          <p class="font-mono text-[0.66rem] tracking-[0.28em] text-ochre-500 uppercase">
            &sect; End of Chapter I
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { h } from 'vue'
import { useI18n } from '../i18n'
const { t } = useI18n()

// Minimal line icons — no emojis. Each is a tiny stateless component.
const stroke = { fill: 'none', stroke: 'currentColor', 'stroke-width': '1.3', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }
const mk = (paths) => () => h('svg', { viewBox: '0 0 24 24', ...stroke, class: 'w-full h-full' },
  paths.map(d => h('path', { d })))

const IconPen      = mk(['M4 20l4-1 11-11a2.83 2.83 0 10-4-4L4 15v5z', 'M13 7l4 4'])
const IconBook     = mk(['M4 5a2 2 0 012-2h12v18H6a2 2 0 01-2-2V5z', 'M18 3v18', 'M8 7h7M8 11h5'])
const IconLoupe    = mk(['M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z', 'M21 21l-5.5-5.5'])
const IconQuill    = mk(['M20 4C12 4 6 9 4 16l-1 4 4-1c7-2 12-8 13-15z', 'M11 13l6-6'])
const IconCompass  = mk(['M12 21a9 9 0 100-18 9 9 0 000 18z', 'M15.5 8.5l-2 5.5-5.5 2 2-5.5 5.5-2z'])
const IconTuning   = mk(['M4 7h16', 'M4 12h16', 'M4 17h16', 'M9 5v4', 'M15 10v4', 'M7 15v4'])

const features = [
  { key: 'corpus', icon: IconPen },
  { key: 'topics', icon: IconBook },
  { key: 'chat',   icon: IconQuill },
  { key: 'rag',    icon: IconLoupe },
  { key: 'notes',  icon: IconCompass },
  { key: 'band',   icon: IconTuning }
]
</script>

<style scoped>
/* The drop-cap paragraph pairs with .ruled-lines for a printed-page feel. */
.ruled-lines {
  padding: .2rem .1rem;
}
</style>
