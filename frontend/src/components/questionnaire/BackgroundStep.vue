<template>
  <div class="space-y-10">
    <!-- Header -->
    <header class="text-center space-y-3">
      <p class="num-chapter">§ 01 · Background</p>
      <h2 class="font-display text-3xl text-ink-900" style="font-variation-settings:'opsz' 96, 'SOFT' 50;">
        个人 <em class="italic text-ochre-500">背景</em>
      </h2>
      <p class="text-ink-500 font-serif italic">告诉我们一些关于你的基本信息 · 所有字段均为可选</p>
    </header>

    <!-- Form -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-7">
      <!-- Age -->
      <div class="space-y-2">
        <label class="field-label">01 · 年龄</label>
        <input
          type="number"
          v-model.number="form.age"
          placeholder="e.g. 22"
          min="10"
          max="80"
          class="input-hairline"
        />
      </div>

      <!-- Gender -->
      <div class="space-y-2">
        <label class="field-label">02 · 性别</label>
        <div class="flex gap-2">
          <button
            v-for="option in genderOptions"
            :key="option.value"
            :class="[
              'flex-1 py-2.5 px-3 text-sm font-serif transition-colors duration-300',
              form.gender === option.value
                ? 'chip-ink-selected'
                : 'hairline text-ink-700 hover:text-ink-900'
            ]"
            @click="form.gender = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <!-- Zodiac -->
      <div class="space-y-2">
        <label class="field-label">03 · 星座</label>
        <select v-model="form.zodiac" class="input-hairline appearance-none">
          <option value="">— 选择你的星座 —</option>
          <option v-for="z in zodiacSigns" :key="z" :value="z">{{ z }}</option>
        </select>
      </div>

      <!-- Profession -->
      <div class="space-y-2">
        <label class="field-label">04 · 职业 / 专业</label>
        <input
          type="text"
          v-model="form.profession"
          placeholder="e.g. 计算机科学 / 软件工程师"
          class="input-hairline"
        />
      </div>

      <!-- City -->
      <div class="space-y-2 md:col-span-2">
        <label class="field-label">05 · 所在城市</label>
        <input
          type="text"
          v-model="form.city"
          placeholder="e.g. 北京 / 上海 / 成都"
          class="input-hairline"
        />
      </div>

      <!-- Self Description -->
      <div class="space-y-2 md:col-span-2">
        <label class="field-label">06 · 自我描述</label>
        <textarea
          v-model="form.selfDescription"
          placeholder="用几句话描述你自己，你的性格特点、生活方式⋯"
          rows="4"
          class="input-hairline resize-none font-serif"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()

const genderOptions = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '不愿透露' }
]

const zodiacSigns = [
  '白羊座', '金牛座', '双子座', '巨蟹座',
  '狮子座', '处女座', '天秤座', '天蝎座',
  '射手座', '摩羯座', '水瓶座', '双鱼座'
]

const form = reactive({
  age: store.personalBackground.age,
  gender: store.personalBackground.gender,
  zodiac: store.personalBackground.zodiac,
  profession: store.personalBackground.profession,
  city: store.personalBackground.city,
  selfDescription: store.personalBackground.selfDescription
})

watch(form, (val) => {
  store.setPersonalBackground({ ...val })
}, { deep: true })
</script>
