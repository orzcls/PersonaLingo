<template>
  <div class="space-y-10">
    <!-- Header -->
    <header class="text-center space-y-3">
      <p class="num-chapter">§ 02 · Personality</p>
      <h2 class="font-display text-3xl text-ink-900" style="font-variation-settings:'opsz' 96, 'SOFT' 50;">
        MBTI <em class="italic text-ochre-500">Profile</em>
      </h2>
      <p class="text-ink-500 font-serif italic">Discover your personality type to personalise your corpus.</p>
    </header>

    <!-- Mode Toggle -->
    <div class="flex justify-center">
      <div class="inline-flex hairline">
        <button
          :class="[
            'px-6 py-2.5 text-sm font-serif transition-colors duration-300',
            mode === 'select' ? 'chip-ink-selected-slim' : 'text-ink-500 hover:text-ink-900'
          ]"
          @click="mode = 'select'"
        >I know my type</button>
        <button
          :class="[
            'px-6 py-2.5 text-sm font-serif transition-colors duration-300',
            mode === 'quiz' ? 'chip-ink-selected-slim' : 'text-ink-500 hover:text-ink-900'
          ]"
          @click="mode = 'quiz'"
        >Quick Assessment</button>
      </div>
    </div>

    <!-- Mode A: Direct MBTI Selection -->
    <section v-if="mode === 'select'" class="space-y-6">
      <p class="text-center text-ink-500 text-sm font-serif italic">Select your MBTI type from the table.</p>
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="type in mbtiTypes"
          :key="type"
          :class="[
            'p-4 text-center transition-colors duration-300',
            store.mbtiResult === type
              ? 'chip-ink-selected'
              : 'hairline text-ink-500 hover:text-ink-900'
          ]"
          @click="selectType(type)"
        >
          <span class="font-display text-lg tracking-wider">{{ type }}</span>
        </button>
      </div>

      <Transition name="fade">
        <div v-if="store.mbtiResult && mode === 'select'" class="paper-card p-6">
          <div class="flex items-baseline gap-3 mb-3">
            <span class="font-display text-3xl italic text-ochre-500">{{ store.mbtiResult }}</span>
            <span class="text-ink-500 font-mono">—</span>
            <span class="font-serif italic text-ink-900 text-lg">{{ mbtiDescriptions[store.mbtiResult]?.title }}</span>
          </div>
          <p class="text-ink-700 text-sm font-serif leading-relaxed">
            <span class="font-display text-2xl italic text-ochre-500 mr-1 leading-none">“</span>{{ mbtiDescriptions[store.mbtiResult]?.desc }}
          </p>
        </div>
      </Transition>
    </section>

    <!-- Mode B: 12-Question Quiz -->
    <section v-if="mode === 'quiz'" class="space-y-6">
      <!-- Quiz progress -->
      <div class="flex items-baseline justify-between text-sm">
        <span class="font-mono text-xs tracking-[0.22em] text-ink-500">
          QUESTION {{ String(currentQuestion + 1).padStart(2, '0') }} / {{ String(mbtiQuestions.length).padStart(2, '0') }}
        </span>
        <span class="font-serif italic text-ochre-500">
          {{ answeredCount }}/12 answered
        </span>
      </div>
      <div class="w-full h-px bg-ink-900/10 relative">
        <div
          class="absolute top-0 left-0 h-px bg-indigo-800 transition-all duration-500"
          :style="{ width: `${(answeredCount / 12) * 100}%` }"
        ></div>
      </div>

      <!-- Question Card -->
      <article class="paper-card p-8">
        <p class="font-display text-xl text-ink-900 mb-6 leading-snug" style="font-variation-settings:'opsz' 96, 'SOFT' 60;">
          {{ mbtiQuestions[currentQuestion].question }}
        </p>
        <div class="space-y-3">
          <button
            v-for="opt in ['a', 'b']"
            :key="opt"
            :class="[
              'w-full text-left p-4 transition-colors duration-300 hairline',
              store.mbtiAnswers[mbtiQuestions[currentQuestion].id] === opt
                ? 'bg-ochre-300/25 hairline-strong text-ink-900'
                : 'text-ink-700 hover:text-ink-900'
            ]"
            @click="answerQuestion(mbtiQuestions[currentQuestion].id, opt)"
          >
            <span class="inline-flex items-baseline gap-3">
              <span :class="[
                'font-display italic text-lg shrink-0',
                store.mbtiAnswers[mbtiQuestions[currentQuestion].id] === opt ? 'text-ochre-500' : 'text-ink-500'
              ]">{{ opt.toUpperCase() }}.</span>
              <span class="font-serif">{{ mbtiQuestions[currentQuestion]['option_' + opt] }}</span>
            </span>
          </button>
        </div>
      </article>

      <!-- Question Navigation -->
      <div class="flex items-center justify-between">
        <button
          :disabled="currentQuestion === 0"
          :class="[
            'px-3 py-2 text-sm font-serif italic transition-colors duration-300',
            currentQuestion === 0 ? 'text-ink-300 cursor-not-allowed' : 'text-ink-500 hover:text-ink-900'
          ]"
          @click="currentQuestion--"
        >← Previous</button>
        <div class="flex gap-2">
          <button
            v-for="(q, idx) in mbtiQuestions"
            :key="q.id"
            :class="[
              'w-2 h-2 rounded-full transition-all duration-300',
              idx === currentQuestion
                ? 'bg-indigo-800 scale-125'
                : store.mbtiAnswers[q.id] ? 'bg-ochre-500' : 'bg-ink-900/15'
            ]"
            @click="currentQuestion = idx"
            :aria-label="'Question ' + (idx + 1)"
          />
        </div>
        <button
          :disabled="currentQuestion === mbtiQuestions.length - 1"
          :class="[
            'px-3 py-2 text-sm font-serif italic transition-colors duration-300',
            currentQuestion === mbtiQuestions.length - 1 ? 'text-ink-300 cursor-not-allowed' : 'text-ink-500 hover:text-ink-900'
          ]"
          @click="currentQuestion++"
        >Next →</button>
      </div>

      <!-- Result -->
      <Transition name="fade">
        <div v-if="answeredCount === 12 && quizResult" class="paper-card p-8">
          <div class="text-center space-y-2">
            <p class="num-chapter">— your result —</p>
            <p class="font-display text-5xl italic text-ochre-500" style="font-variation-settings:'opsz' 144, 'SOFT' 40;">
              {{ quizResult }}
            </p>
            <p class="font-display italic text-ink-900 text-lg">{{ mbtiDescriptions[quizResult]?.title }}</p>
            <p class="text-ink-700 text-sm font-serif leading-relaxed max-w-md mx-auto pt-2">
              {{ mbtiDescriptions[quizResult]?.desc }}
            </p>
          </div>
        </div>
      </Transition>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()
const mode = ref('quiz')
const currentQuestion = ref(0)

const mbtiTypes = [
  'INTJ', 'INTP', 'ENTJ', 'ENTP',
  'INFJ', 'INFP', 'ENFJ', 'ENFP',
  'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
  'ISTP', 'ISFP', 'ESTP', 'ESFP'
]

const mbtiQuestions = [
  { id: 1, dimension: 'EI', question: 'At a party, you tend to:', option_a: 'Talk to many people, including strangers', option_b: 'Talk to a few close friends' },
  { id: 2, dimension: 'EI', question: 'You recharge by:', option_a: 'Going out and socializing', option_b: 'Spending time alone' },
  { id: 3, dimension: 'EI', question: 'In group discussions, you:', option_a: 'Speak up early and often', option_b: 'Listen first, then contribute' },
  { id: 4, dimension: 'SN', question: 'You prefer to focus on:', option_a: 'Present realities and facts', option_b: 'Future possibilities and ideas' },
  { id: 5, dimension: 'SN', question: 'You are more attracted to:', option_a: 'Practical applications', option_b: 'Innovative theories' },
  { id: 6, dimension: 'SN', question: 'You trust more:', option_a: 'Direct experience and observation', option_b: 'Gut feelings and intuition' },
  { id: 7, dimension: 'TF', question: 'When making decisions, you prioritize:', option_a: 'Logic and objective analysis', option_b: 'Personal values and harmony' },
  { id: 8, dimension: 'TF', question: 'You would rather be seen as:', option_a: 'Competent and fair', option_b: 'Warm and empathetic' },
  { id: 9, dimension: 'TF', question: 'In conflicts, you tend to:', option_a: 'Focus on finding the logical solution', option_b: 'Focus on maintaining relationships' },
  { id: 10, dimension: 'JP', question: 'You prefer your schedule to be:', option_a: 'Planned and organized', option_b: 'Flexible and spontaneous' },
  { id: 11, dimension: 'JP', question: 'You feel more comfortable when:', option_a: 'Decisions are made and settled', option_b: 'Options are kept open' },
  { id: 12, dimension: 'JP', question: 'Your workspace is usually:', option_a: 'Neat and systematic', option_b: 'Creative and varied' },
]

const mbtiDescriptions = {
  INTJ: { title: 'The Architect', desc: 'Strategic and independent thinkers with a plan for everything. You approach life with logic and determination.' },
  INTP: { title: 'The Logician', desc: 'Innovative inventors with an unquenchable thirst for knowledge. You love exploring complex theoretical problems.' },
  ENTJ: { title: 'The Commander', desc: 'Bold, imaginative leaders who always find a way. You naturally organize people and processes efficiently.' },
  ENTP: { title: 'The Debater', desc: 'Smart and curious thinkers who love intellectual challenges. You thrive on exploring new ideas.' },
  INFJ: { title: 'The Advocate', desc: 'Quiet and mystical, yet inspiring idealists. You seek meaning and connection in everything.' },
  INFP: { title: 'The Mediator', desc: 'Poetic, kind, and altruistic people who are always eager to help a good cause. You value authenticity deeply.' },
  ENFJ: { title: 'The Protagonist', desc: 'Charismatic and inspiring leaders who mesmerize their listeners. You naturally bring people together.' },
  ENFP: { title: 'The Campaigner', desc: 'Enthusiastic, creative, and sociable free spirits. You always find a reason to smile and share joy.' },
  ISTJ: { title: 'The Logistician', desc: 'Practical and fact-minded individuals whose reliability cannot be doubted. You value tradition and loyalty.' },
  ISFJ: { title: 'The Defender', desc: 'Very dedicated and warm protectors, always ready to defend loved ones. You are nurturing and dependable.' },
  ESTJ: { title: 'The Executive', desc: 'Excellent administrators, managing things and people with clear authority. You value order and structure.' },
  ESFJ: { title: 'The Consul', desc: 'Extraordinarily caring and social, always eager to help. You create harmony in every environment.' },
  ISTP: { title: 'The Virtuoso', desc: 'Bold and practical experimenters, masters of all kinds of tools. You love hands-on problem solving.' },
  ISFP: { title: 'The Adventurer', desc: 'Flexible and charming artists, always ready to explore something new. You live in the present moment.' },
  ESTP: { title: 'The Entrepreneur', desc: 'Smart, energetic, and perceptive people who truly enjoy living on the edge. You love action and excitement.' },
  ESFP: { title: 'The Entertainer', desc: 'Spontaneous, energetic, and enthusiastic entertainers. Life is never boring around you.' },
}

const answeredCount = computed(() => Object.keys(store.mbtiAnswers).length)

const quizResult = computed(() => {
  if (answeredCount.value < 12) return null
  const dimensions = { EI: 0, SN: 0, TF: 0, JP: 0 }
  mbtiQuestions.forEach(q => {
    const answer = store.mbtiAnswers[q.id]
    if (answer === 'a') dimensions[q.dimension]++
  })
  const E = dimensions.EI >= 2 ? 'E' : 'I'
  const S = dimensions.SN >= 2 ? 'S' : 'N'
  const T = dimensions.TF >= 2 ? 'T' : 'F'
  const J = dimensions.JP >= 2 ? 'J' : 'P'
  return E + S + T + J
})

watch(quizResult, (val) => { if (val) store.setMBTIResult(val) })

function selectType(type) { store.setMBTIResult(type) }

function answerQuestion(questionId, answer) {
  store.setMBTIAnswer(questionId, answer)
  if (currentQuestion.value < mbtiQuestions.length - 1) {
    setTimeout(() => {
      const nextUnanswered = mbtiQuestions.findIndex((q, idx) => idx > currentQuestion.value && !store.mbtiAnswers[q.id])
      if (nextUnanswered !== -1) currentQuestion.value = nextUnanswered
      else if (currentQuestion.value < mbtiQuestions.length - 1) currentQuestion.value++
    }, 300)
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s cubic-bezier(.2,.8,.2,1), transform 0.4s cubic-bezier(.2,.8,.2,1);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
