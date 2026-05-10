<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Page Header -->
    <header class="mb-8">
      <p class="num-chapter mb-3">§ 04 · index of questions</p>
      <div class="flex items-end justify-between flex-wrap gap-6">
        <div>
          <h1 class="font-display italic text-4xl md:text-5xl text-ink-900 leading-[1.05]">
            {{ t('topics.title') }}
          </h1>
          <p class="mt-3 font-serif italic text-ink-500 text-sm max-w-xl">
            {{ t('topics.subtitle') }}
          </p>
          <!-- 季度徽标 -->
          <div v-if="meta.current_season" class="mt-4 flex items-center gap-3 text-xs font-mono tracking-wider">
            <span class="px-2 py-1 border border-ink-900/30 text-ink-900">
              {{ t('topics.currentSeason') }} {{ meta.current_season }}
            </span>
            <span v-if="meta.last_updated_at" class="text-ink-500">
              {{ t('topics.lastUpdated') }} {{ formatTime(meta.last_updated_at) }}
            </span>
            <span v-if="meta.stale" class="flex items-center gap-1 text-rouge-600">
              <span class="w-1.5 h-1.5 rounded-full bg-rouge-600 animate-pulse"></span>
              {{ t('topics.staleHint') }}
            </span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <label class="action-btn cursor-pointer">
            <span class="font-mono text-[10px] text-ochre-500 tracking-widest">01</span>
            <span>{{ t('topics.uploadBtn') }}</span>
            <input type="file" accept=".json,.txt,.pdf,.docx,.doc" class="hidden" @change="handleFileUpload" />
          </label>
          <button
            @click="handleScrape"
            :disabled="scrapeLoading"
            class="action-btn disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span class="font-mono text-[10px] text-ochre-500 tracking-widest">02</span>
            <span>{{ scrapeLoading ? t('topics.scraping') : scrapeBtnLabel }}</span>
            <span v-if="scrapeLoading" class="flex gap-0.5 ml-1">
              <span class="w-1 h-1 rounded-full bg-ochre-500 animate-pulse"></span>
              <span class="w-1 h-1 rounded-full bg-ochre-500 animate-pulse" style="animation-delay:.15s"></span>
              <span class="w-1 h-1 rounded-full bg-ochre-500 animate-pulse" style="animation-delay:.3s"></span>
            </span>
          </button>
        </div>
      </div>
      <div class="hairline-strong mt-6"></div>
    </header>

    <!-- Upload Status -->
    <div
      v-if="uploadStatus"
      class="mb-6 p-4 border-l-2 paper-card flex items-center justify-between gap-4"
      :class="statusBarClass(uploadStatus.type)"
    >
      <p class="font-serif italic text-sm text-ink-700">{{ uploadStatus.message }}</p>
      <button @click="uploadStatus = null" class="font-mono text-xs text-ink-500 hover:text-ink-900">×</button>
    </div>

    <!-- Scrape Info -->
    <div
      v-if="scrapeInfo"
      class="mb-6 p-4 border-l-2 paper-card flex items-start justify-between gap-4"
      :class="statusBarClass(scrapeInfo.type)"
    >
      <p class="font-serif italic text-sm text-ink-700 whitespace-pre-line flex-1">{{ scrapeInfo.message }}</p>
      <button @click="scrapeInfo = null" class="font-mono text-xs text-ink-500 hover:text-ink-900 shrink-0">×</button>
    </div>

    <!-- Stats Bar —— 目录式 -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-0 mb-10 border-y border-ink-900/15 py-5">
      <div v-for="(stat, idx) in statList" :key="stat.label" class="px-5" :class="idx !== 0 ? 'md:border-l border-ink-900/10' : ''">
        <p class="num-chapter text-[10px] mb-2">{{ stat.label }}</p>
        <p class="font-display italic text-3xl leading-none" :class="stat.color">
          {{ stat.value }}
        </p>
      </div>
    </div>

    <!-- Search -->
    <div class="mb-6">
      <div class="relative max-w-xl">
        <span class="absolute left-0 top-1/2 -translate-y-1/2 font-mono text-[11px] text-ochre-500 tracking-widest">
          search
        </span>
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('topics.search')"
          class="w-full pl-20 pr-4 py-3 bg-transparent border-b border-ink-900/20 focus:border-ink-900 font-serif italic text-ink-900 placeholder:text-ink-300 focus:outline-none transition-colors"
        />
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="mb-8">
      <TopicFilter :filters="filters" @filter-change="handleFilterChange" />
    </div>

    <!-- Results Count -->
    <div class="mb-5 flex items-center gap-3">
      <span class="hairline flex-1"></span>
      <p class="font-mono text-[11px] text-ink-500 tracking-widest">
        {{ String(filteredTopics.length).padStart(3, '0') }} · topics
      </p>
      <span class="hairline flex-1"></span>
    </div>

    <!-- Topic Cards Grid -->
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4 stagger">
      <TopicCard
        v-for="topic in filteredTopics"
        :key="topic.id"
        :topic="topic"
        :expanded="expandedId === topic.id"
        @toggle="toggleExpand(topic.id)"
      />
    </div>

    <!-- Empty State -->
    <div v-if="filteredTopics.length === 0 && !loading" class="text-center py-20">
      <p class="font-display italic text-2xl text-ink-500 mb-2">
        Nothing filed here yet.
      </p>
      <p class="font-serif italic text-sm text-ink-500">{{ t('topics.emptyHint') }}</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-20">
      <div class="inline-flex gap-2 mb-4">
        <span class="w-2 h-2 rounded-full bg-ink-900 animate-pulse"></span>
        <span class="w-2 h-2 rounded-full bg-ink-900 animate-pulse" style="animation-delay:.2s"></span>
        <span class="w-2 h-2 rounded-full bg-ink-900 animate-pulse" style="animation-delay:.4s"></span>
      </div>
      <p class="font-serif italic text-ink-500 text-sm">{{ t('topics.loading') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TopicCard from '../components/topics/TopicCard.vue'
import TopicFilter from '../components/topics/TopicFilter.vue'
import { getTopics, importTopicsFile, scrapeTopics, getTopicsMeta } from '../api'
import { useRouter } from 'vue-router'
import { useI18n } from '../i18n'

const { t } = useI18n()
const router = useRouter()

const topics = ref([])
const loading = ref(true)
const searchQuery = ref('')
const expandedId = ref(null)
const uploadStatus = ref(null)
const scrapeInfo = ref(null)
const meta = ref({})

const scrapeLoading = ref(false)

const scrapeBtnLabel = computed(() => {
  const season = meta.value.current_season
  if (season) return t('topics.scrapeBtnSeason').replace('{season}', season)
  return t('topics.scrapeBtn')
})

function formatTime(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${y}-${m}-${day}`
  } catch { return iso }
}

const filters = ref({
  part: 'All',
  season: 'All',
  category: 'All'
})

const stats = computed(() => {
  const all = topics.value
  return {
    total: all.length,
    p1: all.filter(t => t.part === 'P1').length,
    p2: all.filter(t => t.part === 'P2').length,
    p3: all.filter(t => t.part === 'P3').length,
    new: all.filter(t => t.is_new).length
  }
})

const statList = computed(() => [
  { label: t('topics.total'), value: pad(stats.value.total), color: 'text-ink-900' },
  { label: 'Part I', value: pad(stats.value.p1), color: 'text-ink-900' },
  { label: 'Part II', value: pad(stats.value.p2), color: 'text-ochre-500' },
  { label: 'Part III', value: pad(stats.value.p3), color: 'text-rouge-600' },
  { label: t('topics.newTopics'), value: pad(stats.value.new), color: 'text-sage-500' }
])

function pad(n) { return String(n).padStart(2, '0') }

const filteredTopics = computed(() => {
  return topics.value.filter(topic => {
    if (searchQuery.value && !topic.title.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    if (filters.value.part !== 'All' && topic.part !== filters.value.part) return false
    if (filters.value.season !== 'All' && topic.season !== filters.value.season) return false
    if (filters.value.category !== 'All' && topic.category !== filters.value.category) return false
    return true
  })
})

function handleFilterChange(newFilters) {
  filters.value = newFilters
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function statusBarClass(type) {
  if (type === 'success') return 'border-sage-500'
  if (type === 'error') return 'border-rouge-600'
  return 'border-ink-900'
}

async function fetchTopics() {
  loading.value = true
  try {
    const response = await getTopics()
    topics.value = response.data || []
  } catch (e) {
    console.error('Failed to fetch topics:', e)
    topics.value = []
  } finally {
    loading.value = false
  }
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  uploadStatus.value = { type: 'info', message: `正在上传 ${file.name}…` }

  try {
    const response = await importTopicsFile(file)
    const data = response.data
    uploadStatus.value = {
      type: 'success',
      message: `上传成功。导入 ${data.imported} 题，跳过 ${data.skipped} 题（重复）${data.errors?.length ? '，' + data.errors.length + ' 个错误' : ''}`
    }
    await fetchTopics()
  } catch (e) {
    uploadStatus.value = {
      type: 'error',
      message: `上传失败：${e.response?.data?.detail || e.message}`
    }
  }

  event.target.value = ''
}

async function fetchMeta() {
  try {
    const response = await getTopicsMeta()
    meta.value = response.data || {}
  } catch (e) {
    console.warn('Failed to fetch topics meta:', e)
    meta.value = {}
  }
}

async function handleScrape() {
  // 未配置搜索或 LLM 则跳转设置页
  if (meta.value && (meta.value.search_provider_configured === false || meta.value.llm_configured === false)) {
    scrapeInfo.value = { type: 'error', message: t('topics.configMissing') }
    setTimeout(() => { router.push('/settings') }, 1200)
    return
  }
  scrapeLoading.value = true
  scrapeInfo.value = null
  try {
    const response = await scrapeTopics()
    const data = response.data || response
    const byPart = data.by_part || {}
    const newP1 = byPart.P1 || 0
    const newP2 = byPart.P2 || 0
    const newP3 = byPart.P3 || 0
    const derived = data.derived_p3 || 0
    const updated = data.updated || 0
    const urls = Array.isArray(data.source_urls) ? data.source_urls.slice(0, 3) : []
    const hasAny = (data.imported || 0) + updated + derived > 0
    if (hasAny) {
      const lines = [
        t('topics.scrapeSuccess')
          .replace('{season}', data.current_season || '-')
          .replace('{p1}', newP1)
          .replace('{p2}', newP2)
          .replace('{p3}', newP3)
          .replace('{derived}', derived)
          .replace('{updated}', updated)
      ]
      if (urls.length) {
        lines.push(t('topics.sources') + ':')
        urls.forEach(u => lines.push(`• ${u}`))
      }
      scrapeInfo.value = { type: 'success', message: lines.join('\n') }
      await Promise.all([fetchTopics(), fetchMeta()])
    } else {
      const errList = data.pipeline_errors || data.errors || []
      const hint = errList.length ? `\n${errList.slice(0, 3).join('\n')}` : ''
      scrapeInfo.value = { type: 'info', message: t('topics.scrapeEmpty') + hint }
    }
  } catch (e) {
    const detail = e.response?.data?.detail || e.message
    scrapeInfo.value = { type: 'error', message: `${t('topics.scrapeFail')}${detail}` }
  } finally {
    scrapeLoading.value = false
  }
}

onMounted(() => {
  fetchTopics()
  fetchMeta()
})
</script>

<style scoped>
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.55rem 1rem;
  border: 1px solid rgba(27, 31, 42, 0.2);
  font-family: 'Fraunces', Georgia, serif;
  font-style: italic;
  font-size: 13px;
  color: var(--ink-700, #2B303C);
  background: var(--paper-50, #FBF7EE);
  transition: border-color .2s ease, color .2s ease, background .2s ease;
}
.action-btn:hover:not(:disabled) {
  border-color: var(--ink-900, #1B1F2A);
  color: var(--ink-900, #1B1F2A);
}
</style>
