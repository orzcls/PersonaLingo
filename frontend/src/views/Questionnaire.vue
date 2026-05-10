<template>
  <div class="max-w-4xl mx-auto px-4 py-14">
    <!-- Page Header -->
    <header class="mb-10">
      <p class="num-chapter mb-3">§ 02 · intake</p>
      <h1 class="font-display italic text-4xl md:text-5xl text-ink-900 leading-[1.05]">
        Tell us who you are
      </h1>
      <p class="mt-3 font-serif italic text-ink-500 text-sm max-w-xl">
        Five short chapters. Answer with the particulars — details make a voice.
      </p>
      <div class="hairline-strong mt-6"></div>
    </header>

    <!-- Progress -->
    <div class="mb-10">
      <ProgressBar :steps="stepNames" :current-step="store.currentStep" />
    </div>

    <!-- Step Content -->
    <article class="paper-card p-8 md:p-10 min-h-[420px]">
      <Transition :name="transitionName" mode="out-in">
        <MBTIStep v-if="store.currentStep === 1" key="mbti" />
        <BackgroundStep v-else-if="store.currentStep === 2" key="background" />
        <InterestStep v-else-if="store.currentStep === 3" key="interest" />
        <ExperienceStep v-else-if="store.currentStep === 4" key="experience" />
        <IELTSStep v-else-if="store.currentStep === 5" key="ielts" />
      </Transition>
    </article>

    <!-- Validation -->
    <Transition name="fade">
      <div
        v-if="validationError"
        class="mt-5 px-5 py-3 border-l-2 border-rouge-600 bg-paper-100/50 font-serif italic text-[14px] text-ink-700"
      >
        {{ validationError }}
      </div>
    </Transition>

    <!-- Navigation -->
    <div class="flex items-center justify-between mt-10">
      <button
        :disabled="store.isFirstStep"
        class="nav-btn"
        :class="store.isFirstStep ? 'is-disabled' : ''"
        @click="handlePrev"
      >
        <span class="text-ochre-500 mr-1">←</span> Previous
      </button>

      <span class="font-mono text-[11px] text-ink-500 tracking-widest">
        {{ String(store.currentStep).padStart(2, '0') }} / {{ String(stepNames.length).padStart(2, '0') }}
      </span>

      <button
        :disabled="isSubmitting"
        class="btn-ink"
        :class="isSubmitting ? 'opacity-50 cursor-not-allowed' : ''"
        @click="handleNext"
      >
        <span v-if="isSubmitting" class="inline-flex items-center gap-2">
          <span class="flex gap-0.5">
            <span class="w-1 h-1 rounded-full bg-ochre-300 animate-pulse"></span>
            <span class="w-1 h-1 rounded-full bg-ochre-300 animate-pulse" style="animation-delay:.15s"></span>
            <span class="w-1 h-1 rounded-full bg-ochre-300 animate-pulse" style="animation-delay:.3s"></span>
          </span>
          Submitting
        </span>
        <template v-else>
          <span>{{ store.isLastStep ? 'Submit & Compose' : 'Next' }}</span>
          <span class="text-ochre-300">→</span>
        </template>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ProgressBar from '../components/ProgressBar.vue'
import MBTIStep from '../components/questionnaire/MBTIStep.vue'
import BackgroundStep from '../components/questionnaire/BackgroundStep.vue'
import InterestStep from '../components/questionnaire/InterestStep.vue'
import ExperienceStep from '../components/questionnaire/ExperienceStep.vue'
import IELTSStep from '../components/questionnaire/IELTSStep.vue'
import { useQuestionnaireStore } from '../stores/questionnaire'
import { submitQuestionnaire } from '../api/index.js'

const store = useQuestionnaireStore()
const router = useRouter()

const stepNames = ['Personality', 'Background', 'Interests', 'Experience', 'Target']
const validationError = ref('')
const isSubmitting = ref(false)
const transitionName = ref('slide-left')

function validateCurrentStep() {
  validationError.value = ''
  if (store.currentStep === 1) {
    if (!store.mbtiResult) {
      validationError.value = 'Please select your MBTI type or complete the quiz.'
      return false
    }
  }
  if (store.currentStep === 5) {
    if (!store.ieltsPreference.targetBand) {
      validationError.value = 'Please select a target band score.'
      return false
    }
    if (store.ieltsPreference.topicTypes.length === 0) {
      validationError.value = 'Please select at least one topic type.'
      return false
    }
  }
  return true
}

function handlePrev() {
  transitionName.value = 'slide-right'
  validationError.value = ''
  store.prevStep()
}

async function handleNext() {
  if (!validateCurrentStep()) return
  if (store.isLastStep) {
    await handleSubmit()
  } else {
    transitionName.value = 'slide-left'
    store.nextStep()
  }
}

async function handleSubmit() {
  isSubmitting.value = true
  validationError.value = ''
  try {
    const payload = {
      mbti: {
        mode: store.mbtiResult ? 'direct' : 'test',
        type_code: store.mbtiResult,
        answers: store.mbtiAnswers
      },
      interests: {
        tags: store.interests.tags,
        descriptions: store.interests.descriptions.filter(d => d.trim())
      },
      ielts: {
        target_score: store.ieltsPreference.targetBand,
        topic_types: store.ieltsPreference.topicTypes,
        exam_date: store.ieltsPreference.examMonth
      },
      personal_background: store.personalBackground,
      life_experiences: store.lifeExperiences
    }
    const response = await submitQuestionnaire(payload)
    store.setQuestionnaireId(response.id || response.questionnaire_id)
    router.push('/generating')
  } catch (error) {
    console.error('Submit error:', error)
    validationError.value = 'Failed to submit questionnaire. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.nav-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.55rem 0;
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 15px;
  color: var(--ink-700, #2B303C);
  transition: color .2s ease;
}
.nav-btn:hover:not(.is-disabled) { color: var(--ink-900, #1B1F2A); }
.nav-btn.is-disabled {
  color: var(--ink-300, #A7ABB3);
  cursor: not-allowed;
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.35s cubic-bezier(.2,.8,.2,1);
}
.slide-left-enter-from { opacity: 0; transform: translateX(24px); }
.slide-left-leave-to { opacity: 0; transform: translateX(-24px); }
.slide-right-enter-from { opacity: 0; transform: translateX(-24px); }
.slide-right-leave-to { opacity: 0; transform: translateX(24px); }

.fade-enter-active,
.fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
