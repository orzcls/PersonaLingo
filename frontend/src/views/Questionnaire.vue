<template>
  <div class="max-w-4xl mx-auto px-4 py-12">
    <!-- Progress Bar -->
    <div class="mb-12">
      <ProgressBar :steps="stepNames" :current-step="store.currentStep" />
    </div>

    <!-- Step Content -->
    <div class="bg-dark-800/50 border border-dark-700 rounded-2xl p-8 min-h-[400px]">
      <Transition :name="transitionName" mode="out-in">
        <MBTIStep v-if="store.currentStep === 1" key="mbti" />
        <InterestStep v-else-if="store.currentStep === 2" key="interest" />
        <IELTSStep v-else-if="store.currentStep === 3" key="ielts" />
      </Transition>
    </div>

    <!-- Validation Message -->
    <Transition name="fade">
      <div v-if="validationError" class="mt-4 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm text-center">
        {{ validationError }}
      </div>
    </Transition>

    <!-- Navigation Buttons -->
    <div class="flex justify-between mt-8">
      <button
        :disabled="store.isFirstStep"
        :class="[
          'px-6 py-3 rounded-xl font-medium transition-all duration-200',
          store.isFirstStep
            ? 'bg-dark-800 text-dark-500 cursor-not-allowed'
            : 'bg-dark-700 text-white hover:bg-dark-600'
        ]"
        @click="handlePrev"
      >
        ← Previous
      </button>

      <button
        :disabled="isSubmitting"
        :class="[
          'px-6 py-3 rounded-xl font-medium transition-all duration-200',
          store.isLastStep
            ? 'bg-gradient-to-r from-accent-500 to-secondary-500 text-white shadow-lg shadow-accent-500/25 hover:shadow-accent-500/40'
            : 'bg-accent-500 text-white hover:bg-accent-600',
          isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
        ]"
        @click="handleNext"
      >
        <span v-if="isSubmitting" class="inline-flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Submitting...
        </span>
        <span v-else>{{ store.isLastStep ? 'Submit & Generate' : 'Next →' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ProgressBar from '../components/ProgressBar.vue'
import MBTIStep from '../components/questionnaire/MBTIStep.vue'
import InterestStep from '../components/questionnaire/InterestStep.vue'
import IELTSStep from '../components/questionnaire/IELTSStep.vue'
import { useQuestionnaireStore } from '../stores/questionnaire'
import { submitQuestionnaire } from '../api/index.js'

const store = useQuestionnaireStore()
const router = useRouter()

const stepNames = ['MBTI Profile', 'Interests', 'IELTS Preferences']
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

  if (store.currentStep === 2) {
    if (store.interests.tags.length < 3) {
      validationError.value = 'Please select at least 3 interest tags.'
      return false
    }
  }

  if (store.currentStep === 3) {
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
      mbti_type: store.mbtiResult,
      mbti_answers: store.mbtiAnswers,
      interests: {
        tags: store.interests.tags,
        descriptions: store.interests.descriptions.filter(d => d.trim())
      },
      ielts_preference: {
        target_band: store.ieltsPreference.targetBand,
        topic_types: store.ieltsPreference.topicTypes,
        exam_month: store.ieltsPreference.examMonth
      }
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
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
