<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="text-center">
      <h2 class="text-2xl font-bold text-white mb-2">MBTI Personality Profile</h2>
      <p class="text-dark-400">Discover your personality type to personalize your corpus</p>
    </div>

    <!-- Mode Toggle -->
    <div class="flex justify-center">
      <div class="inline-flex bg-dark-800 rounded-xl p-1">
        <button
          :class="[
            'px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
            mode === 'select'
              ? 'bg-accent-500 text-white shadow-lg shadow-accent-500/25'
              : 'text-dark-400 hover:text-white'
          ]"
          @click="mode = 'select'"
        >
          I know my type
        </button>
        <button
          :class="[
            'px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
            mode === 'quiz'
              ? 'bg-accent-500 text-white shadow-lg shadow-accent-500/25'
              : 'text-dark-400 hover:text-white'
          ]"
          @click="mode = 'quiz'"
        >
          Quick Assessment
        </button>
      </div>
    </div>

    <!-- Mode A: Direct MBTI Selection (16-grid) -->
    <div v-if="mode === 'select'" class="space-y-6">
      <p class="text-center text-dark-400 text-sm">Select your MBTI type</p>
      <div class="grid grid-cols-4 gap-3">
        <button
          v-for="type in mbtiTypes"
          :key="type"
          :class="[
            'p-4 rounded-xl border-2 text-center font-bold transition-all duration-200',
            store.mbtiResult === type
              ? 'border-accent-400 bg-accent-400/10 text-accent-400 shadow-lg shadow-accent-500/10'
              : 'border-dark-700 bg-dark-800 text-dark-300 hover:border-dark-500 hover:text-white'
          ]"
          @click="selectType(type)"
        >
          {{ type }}
        </button>
      </div>

      <!-- Selected type description -->
      <Transition name="fade">
        <div v-if="store.mbtiResult && mode === 'select'" class="bg-dark-800 rounded-xl p-6 border border-accent-400/20">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-2xl font-bold text-accent-400">{{ store.mbtiResult }}</span>
            <span class="text-dark-400">—</span>
            <span class="text-white font-medium">{{ mbtiDescriptions[store.mbtiResult]?.title }}</span>
          </div>
          <p class="text-dark-300 text-sm leading-relaxed">{{ mbtiDescriptions[store.mbtiResult]?.desc }}</p>
        </div>
      </Transition>
    </div>

    <!-- Mode B: 12-Question Quiz -->
    <div v-if="mode === 'quiz'" class="space-y-6">
      <!-- Quiz progress -->
      <div class="flex items-center justify-between text-sm">
        <span class="text-dark-400">Question {{ currentQuestion + 1 }} of {{ mbtiQuestions.length }}</span>
        <span class="text-accent-400 font-medium">{{ answeredCount }}/12 answered</span>
      </div>
      <div class="w-full h-1.5 bg-dark-800 rounded-full overflow-hidden">
        <div
          class="h-full bg-gradient-to-r from-accent-500 to-secondary-500 rounded-full transition-all duration-300"
          :style="{ width: `${(answeredCount / 12) * 100}%` }"
        />
      </div>

      <!-- Question Card -->
      <div class="bg-dark-800 rounded-xl p-6 border border-dark-700">
        <p class="text-white text-lg font-medium mb-6">{{ mbtiQuestions[currentQuestion].question }}</p>
        <div class="space-y-3">
          <button
            :class="[
              'w-full text-left p-4 rounded-xl border-2 transition-all duration-200',
              store.mbtiAnswers[mbtiQuestions[currentQuestion].id] === 'a'
                ? 'border-accent-400 bg-accent-400/10 text-white'
                : 'border-dark-700 bg-dark-900 text-dark-300 hover:border-dark-500 hover:text-white'
            ]"
            @click="answerQuestion(mbtiQuestions[currentQuestion].id, 'a')"
          >
            <span class="inline-flex items-center gap-3">
              <span :class="[
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                store.mbtiAnswers[mbtiQuestions[currentQuestion].id] === 'a'
                  ? 'bg-accent-400 text-dark-900'
                  : 'bg-dark-700 text-dark-400'
              ]">A</span>
              <span>{{ mbtiQuestions[currentQuestion].option_a }}</span>
            </span>
          </button>
          <button
            :class="[
              'w-full text-left p-4 rounded-xl border-2 transition-all duration-200',
              store.mbtiAnswers[mbtiQuestions[currentQuestion].id] === 'b'
                ? 'border-accent-400 bg-accent-400/10 text-white'
                : 'border-dark-700 bg-dark-900 text-dark-300 hover:border-dark-500 hover:text-white'
            ]"
            @click="answerQuestion(mbtiQuestions[currentQuestion].id, 'b')"
          >
            <span class="inline-flex items-center gap-3">
              <span :class="[
                'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0',
                store.mbtiAnswers[mbtiQuestions[currentQuestion].id] === 'b'
                  ? 'bg-accent-400 text-dark-900'
                  : 'bg-dark-700 text-dark-400'
              ]">B</span>
              <span>{{ mbtiQuestions[currentQuestion].option_b }}</span>
            </span>
          </button>
        </div>
      </div>

      <!-- Question Navigation -->
      <div class="flex items-center justify-between">
        <button
          :disabled="currentQuestion === 0"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
            currentQuestion === 0
              ? 'text-dark-600 cursor-not-allowed'
              : 'text-dark-300 hover:text-white hover:bg-dark-700'
          ]"
          @click="currentQuestion--"
        >
          ← Previous
        </button>
        <div class="flex gap-1.5">
          <button
            v-for="(q, idx) in mbtiQuestions"
            :key="q.id"
            :class="[
              'w-2.5 h-2.5 rounded-full transition-all duration-200',
              idx === currentQuestion
                ? 'bg-accent-400 scale-125'
                : store.mbtiAnswers[q.id]
                  ? 'bg-accent-400/40'
                  : 'bg-dark-700'
            ]"
            @click="currentQuestion = idx"
          />
        </div>
        <button
          :disabled="currentQuestion === mbtiQuestions.length - 1"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
            currentQuestion === mbtiQuestions.length - 1
              ? 'text-dark-600 cursor-not-allowed'
              : 'text-dark-300 hover:text-white hover:bg-dark-700'
          ]"
          @click="currentQuestion++"
        >
          Next →
        </button>
      </div>

      <!-- Result (shown when all 12 answered) -->
      <Transition name="fade">
        <div v-if="answeredCount === 12 && quizResult" class="bg-dark-800 rounded-xl p-6 border border-accent-400/30">
          <div class="text-center">
            <p class="text-dark-400 text-sm mb-2">Your Result</p>
            <p class="text-4xl font-bold text-accent-400 mb-2">{{ quizResult }}</p>
            <p class="text-white font-medium mb-1">{{ mbtiDescriptions[quizResult]?.title }}</p>
            <p class="text-dark-300 text-sm leading-relaxed max-w-md mx-auto">{{ mbtiDescriptions[quizResult]?.desc }}</p>
          </div>
        </div>
      </Transition>
    </div>
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

// Auto-set mbtiResult when quiz is complete
watch(quizResult, (val) => {
  if (val) store.setMBTIResult(val)
})

function selectType(type) {
  store.setMBTIResult(type)
}

function answerQuestion(questionId, answer) {
  store.setMBTIAnswer(questionId, answer)
  // Auto-advance to next unanswered question
  if (currentQuestion.value < mbtiQuestions.length - 1) {
    setTimeout(() => {
      const nextUnanswered = mbtiQuestions.findIndex((q, idx) => idx > currentQuestion.value && !store.mbtiAnswers[q.id])
      if (nextUnanswered !== -1) {
        currentQuestion.value = nextUnanswered
      } else if (currentQuestion.value < mbtiQuestions.length - 1) {
        currentQuestion.value++
      }
    }, 300)
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
