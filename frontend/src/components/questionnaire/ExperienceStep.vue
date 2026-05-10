<template>
  <div class="space-y-10">
    <!-- Header -->
    <header class="text-center space-y-3">
      <p class="num-chapter">§ 05 · Real experiences</p>
      <h2 class="font-display text-3xl text-ink-900" style="font-variation-settings:'opsz' 96, 'SOFT' 50;">
        真实 <em class="italic text-ochre-500">经历</em>
      </h2>
      <p class="text-ink-500 font-serif italic">分享你生活中重要的人、物、地 · 让语料更生动真实</p>
    </header>

    <!-- Tab Navigation -->
    <div class="flex hairline-b">
      <button
        v-for="(tab, idx) in tabs"
        :key="tab.key"
        :class="[
          'flex-1 py-3 px-4 text-center transition-colors duration-300 relative',
          activeTab === tab.key ? 'text-ink-900' : 'text-ink-500 hover:text-ink-700'
        ]"
        @click="activeTab = tab.key"
      >
        <span class="font-mono text-[10px] tracking-[0.22em] text-ochre-500 mr-2">{{ String(idx + 1).padStart(2, '0') }}</span>
        <span class="font-display italic text-base">{{ tab.label }}</span>
        <span v-if="activeTab === tab.key" class="absolute left-1/2 -translate-x-1/2 bottom-0 h-[2px] w-10 bg-ochre-500"></span>
      </button>
    </div>

    <!-- People Tab -->
    <div v-show="activeTab === 'people'" class="space-y-4 stagger">
      <div v-if="people.length === 0" class="text-center py-12 paper-card-muted">
        <p class="num-chapter mb-3">— empty —</p>
        <p class="font-serif italic text-ink-500 px-8">
          添加你生活中重要的人，这些真实经历将帮助生成更地道的口语语料。
        </p>
      </div>

      <article v-for="(person, index) in people" :key="'person-' + index" class="paper-card p-6 relative">
        <button
          @click="removePerson(index)"
          class="absolute top-3 right-3 w-7 h-7 text-ink-500 hover:text-rouge-600 transition-colors font-mono text-lg"
          aria-label="remove"
        >×</button>

        <div class="flex items-baseline gap-3 mb-4">
          <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
            P.{{ String(index + 1).padStart(2, '0') }}
          </span>
          <span class="flex-1 h-px bg-ink-900/10"></span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="space-y-1.5">
            <label class="field-label">关系类型</label>
            <select v-model="person.relationship" class="input-hairline appearance-none">
              <option value="">— 选择关系 —</option>
              <option v-for="r in relationshipTypes" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="field-label">称呼</label>
            <input v-model="person.nickname" placeholder="你怎么称呼 ta" class="input-hairline" />
          </div>
        </div>
        <div class="space-y-1.5 mt-5">
          <label class="field-label">描述 · 故事</label>
          <textarea
            v-model="person.description"
            placeholder="这个人的特点或你们之间的故事⋯"
            rows="3"
            class="input-hairline resize-none font-serif"
          />
        </div>
      </article>

      <button
        v-if="people.length < 5"
        @click="addPerson"
        class="w-full py-4 hairline border-dashed text-ink-500 hover:text-ink-900 transition-colors font-serif italic text-sm"
        style="border-style: dashed;"
      >
        ＋ 添加一位重要的人
      </button>
    </div>

    <!-- Objects Tab -->
    <div v-show="activeTab === 'objects'" class="space-y-4 stagger">
      <div v-if="objects.length === 0" class="text-center py-12 paper-card-muted">
        <p class="num-chapter mb-3">— empty —</p>
        <p class="font-serif italic text-ink-500 px-8">
          添加对你有意义的物品，它们的故事能让口语表达更生动真实。
        </p>
      </div>

      <article v-for="(obj, index) in objects" :key="'obj-' + index" class="paper-card p-6 relative">
        <button
          @click="removeObject(index)"
          class="absolute top-3 right-3 w-7 h-7 text-ink-500 hover:text-rouge-600 transition-colors font-mono text-lg"
          aria-label="remove"
        >×</button>

        <div class="flex items-baseline gap-3 mb-4">
          <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
            O.{{ String(index + 1).padStart(2, '0') }}
          </span>
          <span class="flex-1 h-px bg-ink-900/10"></span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="space-y-1.5">
            <label class="field-label">类别</label>
            <select v-model="obj.category" class="input-hairline appearance-none">
              <option value="">— 选择类别 —</option>
              <option v-for="c in objectCategories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="field-label">名称</label>
            <input v-model="obj.name" placeholder="物品的名字" class="input-hairline" />
          </div>
        </div>
        <div class="space-y-1.5 mt-5">
          <label class="field-label">意义</label>
          <textarea
            v-model="obj.significance"
            placeholder="这个物品为什么对你重要⋯"
            rows="3"
            class="input-hairline resize-none font-serif"
          />
        </div>
      </article>

      <button
        v-if="objects.length < 5"
        @click="addObject"
        class="w-full py-4 hairline border-dashed text-ink-500 hover:text-ink-900 transition-colors font-serif italic text-sm"
        style="border-style: dashed;"
      >
        ＋ 添加一件有意义的物
      </button>
    </div>

    <!-- Places Tab -->
    <div v-show="activeTab === 'places'" class="space-y-4 stagger">
      <div v-if="places.length === 0" class="text-center py-12 paper-card-muted">
        <p class="num-chapter mb-3">— empty —</p>
        <p class="font-serif italic text-ink-500 px-8">
          添加印象深刻的地方，真实的旅行和生活经历是最好的口语素材。
        </p>
      </div>

      <article v-for="(place, index) in places" :key="'place-' + index" class="paper-card p-6 relative">
        <button
          @click="removePlace(index)"
          class="absolute top-3 right-3 w-7 h-7 text-ink-500 hover:text-rouge-600 transition-colors font-mono text-lg"
          aria-label="remove"
        >×</button>

        <div class="flex items-baseline gap-3 mb-4">
          <span class="font-mono text-xs tracking-[0.22em] text-ochre-500">
            L.{{ String(index + 1).padStart(2, '0') }}
          </span>
          <span class="flex-1 h-px bg-ink-900/10"></span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="space-y-1.5">
            <label class="field-label">类别</label>
            <select v-model="place.category" class="input-hairline appearance-none">
              <option value="">— 选择类别 —</option>
              <option v-for="c in placeCategories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="field-label">名称</label>
            <input v-model="place.name" placeholder="地点名称" class="input-hairline" />
          </div>
        </div>
        <div class="space-y-1.5 mt-5">
          <label class="field-label">经历</label>
          <textarea
            v-model="place.experience"
            placeholder="在这里的经历和感受⋯"
            rows="3"
            class="input-hairline resize-none font-serif"
          />
        </div>
      </article>

      <button
        v-if="places.length < 5"
        @click="addPlace"
        class="w-full py-4 hairline border-dashed text-ink-500 hover:text-ink-900 transition-colors font-serif italic text-sm"
        style="border-style: dashed;"
      >
        ＋ 添加一个印象深刻的地方
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useQuestionnaireStore } from '../../stores/questionnaire'

const store = useQuestionnaireStore()

const tabs = [
  { key: 'people', label: 'People' },
  { key: 'objects', label: 'Objects' },
  { key: 'places', label: 'Places' }
]

const relationshipTypes = ['挚友', '对象', '家人', '导师', '同学', '室友', '宠物']
const objectCategories = ['乐器', '书', '宠物', '车', '礼物', '收藏品', '电子设备', '运动器材']
const placeCategories = ['山水名胜', '国家城市', '博物馆', '公园', '校园', '餐厅咖啡店', '旅行目的地']

const activeTab = ref('people')

const people = ref(store.lifeExperiences.people.length > 0 ? [...store.lifeExperiences.people] : [])
const objects = ref(store.lifeExperiences.objects.length > 0 ? [...store.lifeExperiences.objects] : [])
const places = ref(store.lifeExperiences.places.length > 0 ? [...store.lifeExperiences.places] : [])

function addPerson() {
  if (people.value.length < 5) people.value.push({ relationship: '', nickname: '', description: '' })
}
function removePerson(index) { people.value.splice(index, 1) }
function addObject() {
  if (objects.value.length < 5) objects.value.push({ category: '', name: '', significance: '' })
}
function removeObject(index) { objects.value.splice(index, 1) }
function addPlace() {
  if (places.value.length < 5) places.value.push({ category: '', name: '', experience: '' })
}
function removePlace(index) { places.value.splice(index, 1) }

watch(people, (val) => { store.setLifeExperiences({ people: [...val] }) }, { deep: true })
watch(objects, (val) => { store.setLifeExperiences({ objects: [...val] }) }, { deep: true })
watch(places, (val) => { store.setLifeExperiences({ places: [...val] }) }, { deep: true })
</script>
