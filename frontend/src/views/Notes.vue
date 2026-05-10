<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Page Header -->
    <header class="mb-10" v-if="!expandedNote">
      <p class="num-chapter mb-3">§ 05 · margin notes</p>
      <h1 class="font-display italic text-4xl md:text-5xl text-ink-900 leading-[1.05]">
        {{ t('notes.title') }}
      </h1>
      <p class="mt-3 font-serif italic text-ink-500 text-sm max-w-xl">
        {{ t('notes.subtitle') }}
      </p>
      <div class="hairline-strong mt-6"></div>
    </header>

    <!-- Notes List (timeline) -->
    <div v-if="!expandedNote">
      <div class="relative pl-6 md:pl-10">
        <!-- 垂直时间线 -->
        <span class="absolute left-1 md:left-3 top-3 bottom-3 w-px bg-ink-900/15"></span>

        <transition-group name="list" tag="div" class="space-y-5">
          <div v-for="note in notes" :key="note.id" class="relative">
            <!-- 节点 -->
            <span class="absolute -left-[calc(1.5rem+1px)] md:-left-[calc(2.5rem+1px)] top-5 w-2.5 h-2.5 rotate-45 bg-ochre-500"></span>
            <NoteCard :note="note" @expand="expandNote" />
          </div>
        </transition-group>

        <!-- Empty State -->
        <div v-if="notes.length === 0" class="text-center py-20">
          <p class="font-display italic text-2xl text-ink-500 mb-2">
            No margin notes yet.
          </p>
          <p class="font-serif italic text-sm text-ink-500">{{ t('notes.emptyHint') }}</p>
        </div>
      </div>
    </div>

    <!-- Expanded Note Detail -->
    <div v-if="expandedNote" class="space-y-8">
      <!-- Back Link -->
      <button
        @click="expandedNote = null"
        class="inline-flex items-center gap-2 font-serif italic text-sm text-ink-500 hover:text-ink-900 transition-colors"
      >
        <span class="text-ochre-500">←</span>
        {{ t('notes.backToNotes') }}
      </button>

      <!-- Detail Header -->
      <div>
        <div class="flex items-baseline justify-between flex-wrap gap-3 mb-3">
          <p class="num-chapter text-[11px]">
            § note · {{ formatChapter(expandedNote.created_at) }}
          </p>
          <span class="font-mono text-[10px] tracking-widest" :class="triggerColor(expandedNote.trigger_type)">
            {{ expandedNote.trigger_type?.toUpperCase() }}
          </span>
        </div>
        <h1 class="font-display italic text-4xl md:text-5xl text-ink-900 leading-[1.1]">
          {{ expandedNote.title }}
        </h1>
        <div class="hairline mt-6"></div>
      </div>

      <!-- Summary：drop-cap 首字下沉 -->
      <article class="paper-card p-7 md:p-10">
        <p class="font-serif text-[16px] leading-[1.95] text-ink-700 drop-cap">
          {{ expandedNote.summary }}
        </p>
      </article>

      <!-- Changes Section -->
      <section v-if="expandedNote.changes?.length" class="paper-card p-7 md:p-10">
        <div class="flex items-center gap-4 mb-5">
          <span class="font-mono text-ochre-500 text-[10px] tracking-widest">—</span>
          <h3 class="font-display italic text-xl text-ink-900">{{ t('notes.changes') }}</h3>
          <span class="hairline flex-1"></span>
        </div>
        <ol class="space-y-3">
          <li
            v-for="(change, idx) in expandedNote.changes"
            :key="'c-' + idx"
            class="flex items-start gap-4"
          >
            <span class="font-mono text-ochre-500 text-[11px] tracking-widest shrink-0 pt-1">
              {{ String(idx + 1).padStart(2, '0') }}
            </span>
            <span class="font-serif text-[15px] leading-[1.85] text-ink-700">{{ change }}</span>
          </li>
        </ol>
      </section>

      <!-- Tips Section -->
      <section v-if="expandedNote.tips?.length" class="paper-card p-7 md:p-10">
        <div class="flex items-center gap-4 mb-5">
          <span class="font-mono text-ochre-500 text-[10px] tracking-widest">—</span>
          <h3 class="font-display italic text-xl text-ink-900">{{ t('notes.tips') }}</h3>
          <span class="hairline flex-1"></span>
        </div>
        <ul class="space-y-3">
          <li
            v-for="(tip, idx) in expandedNote.tips"
            :key="'t-' + idx"
            class="flex items-start gap-4"
          >
            <span class="font-display italic text-ochre-500 text-xl leading-none shrink-0 pt-1">§</span>
            <span class="font-serif italic text-[15px] leading-[1.85] text-ink-700">{{ tip }}</span>
          </li>
        </ul>
      </section>

      <!-- Mind Map -->
      <section v-if="expandedNote.mindmap_mermaid" class="paper-card p-7 md:p-10">
        <div class="flex items-center gap-4 mb-5">
          <span class="font-mono text-sage-500 text-[10px] tracking-widest">—</span>
          <h3 class="font-display italic text-xl text-ink-900">{{ t('notes.mindmap') }}</h3>
          <span class="hairline flex-1"></span>
        </div>
        <MindMap :mermaid-code="expandedNote.mindmap_mermaid" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NoteCard from '../components/notes/NoteCard.vue'
import MindMap from '../components/notes/MindMap.vue'
import { useI18n } from '../i18n'

const { t } = useI18n()

const expandedNote = ref(null)

// Mock data
const notes = ref([
  {
    id: 1,
    title: 'Hometown Topic — Vocabulary Expansion',
    summary: 'Added new descriptive vocabulary and improved sentence structure for describing hometown features. Focus on natural transitions between ideas.',
    trigger_type: 'conversation',
    created_at: '2025-05-07T14:30:00Z',
    changes: [
      'Added 5 new descriptive adjectives for city features',
      'Improved transition phrases between hometown aspects',
      'Refined pronunciation notes for key vocabulary'
    ],
    tips: [
      'Use "bustling" instead of "busy" for more vivid description',
      'Connect childhood memories to current feelings about hometown',
      'Practice the "not only…but also" structure for balanced answers'
    ],
    mindmap_mermaid: `graph TD
    A[Hometown] --> B[Location]
    A --> C[Features]
    A --> D[Feelings]
    B --> B1[Province]
    B --> B2[Geography]
    C --> C1[Food]
    C --> C2[Culture]
    C --> C3[People]
    D --> D1[Nostalgia]
    D --> D2[Pride]`
  },
  {
    id: 2,
    title: 'Music & Entertainment — Pattern Practice',
    summary: 'Practiced expressing preferences using comparative structures. Added bridging phrases to connect personal experience with general opinions.',
    trigger_type: 'practice',
    created_at: '2025-05-06T10:15:00Z',
    changes: [
      'Learned 3 new comparative sentence patterns',
      'Added music genre vocabulary with examples',
      'Created answer templates for "why" follow-up questions'
    ],
    tips: [
      'Always give a reason after stating preference',
      'Use personal anecdotes to make answers memorable',
      'Vary your sentence openings to avoid repetition'
    ],
    mindmap_mermaid: `graph TD
    A[Music Preferences] --> B[Genres]
    A --> C[Activities]
    A --> D[Memories]
    B --> B1[Pop]
    B --> B2[Classical]
    B --> B3[Jazz]
    C --> C1[Listening]
    C --> C2[Concerts]
    D --> D1[Childhood]
    D --> D2[Recent]`
  },
  {
    id: 3,
    title: 'Speaking Fluency — Review Notes',
    summary: 'Weekly review of speaking patterns. Identified areas needing improvement in coherence and lexical resource scores.',
    trigger_type: 'review',
    created_at: '2025-05-05T16:45:00Z',
    changes: [
      'Identified 3 common filler word patterns to eliminate',
      'Marked vocabulary items that need more practice',
      'Updated difficulty ratings for practiced topics'
    ],
    tips: [
      'Record yourself and listen for unnecessary pauses',
      'Practice topic transitions with a timer (2 min max)',
      'Focus on one improvement area per practice session'
    ],
    mindmap_mermaid: null
  }
])

function expandNote(note) {
  expandedNote.value = note
}

function formatChapter(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return `${date.getFullYear()}·${String(date.getMonth() + 1).padStart(2, '0')}·${String(date.getDate()).padStart(2, '0')}`
}

function triggerColor(type) {
  const map = {
    conversation: 'text-ink-500',
    practice: 'text-ochre-500',
    review: 'text-sage-500',
    auto: 'text-ink-500'
  }
  return map[type] || 'text-ink-500'
}
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all .35s cubic-bezier(.2,.8,.2,1);
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
