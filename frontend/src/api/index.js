import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// MBTI 相关
export function getMBTIQuestions() {
  return api.get('/questionnaire/mbti-questions')
}

// 兴趣标签
export function getInterestTags() {
  return api.get('/questionnaire/interest-tags')
}

// 提交问卷
export function submitQuestionnaire(data) {
  return api.post('/questionnaire/submit', data)
}

// 生成语料库
export function generateCorpus(questionnaireId) {
  return api.post('/corpus/generate', { questionnaire_id: questionnaireId })
}

// 获取语料库
export function getCorpus(corpusId) {
  return api.get(`/corpus/${corpusId}`)
}

// === 新增 Topics API ===
export function getTopics(params = {}) {
  return api.get('/topics', { params })
}
export function getTopicStats() {
  return api.get('/topics/stats')
}
export function getTopicCategories() {
  return api.get('/topics/categories')
}
export function getTopicSeasons() {
  return api.get('/topics/seasons')
}
export function importTopicsFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/topics/import/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}
export function scrapeTopics() {
  return api.post('/topics/scrape', null, {
    timeout: 120000
  })
}
export function getTopicsMeta() {
  return api.get('/topics/meta')
}
export function backfillP3(limit = 20) {
  return api.post('/topics/backfill-p3', null, { params: { limit }, timeout: 120000 })
}

// === 新增 Materials API ===
export function uploadMaterial(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/materials/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
export function getMaterials() {
  return api.get('/materials')
}
export function analyzeMaterial(materialId) {
  return api.post(`/materials/${materialId}/analyze`)
}
export function mergeMaterial(materialId, corpusId, selectedItems = null) {
  return api.post(`/materials/${materialId}/merge`, {
    corpus_id: corpusId,
    selected_items: selectedItems,
  })
}

// === 新增 Conversation API ===
export function sendChatMessage(corpusId, content) {
  return api.post(`/conversations/${corpusId}/chat`, { content })
}
export function getChatHistory(corpusId, limit = 50) {
  return api.get(`/conversations/${corpusId}/history`, { params: { limit } })
}
export function extractFromConversation(corpusId, data) {
  return api.post(`/conversations/${corpusId}/extract`, data)
}
export function mergeExtracted(corpusId, items) {
  return api.post(`/conversations/${corpusId}/merge`, items)
}
export function getUserStyle(corpusId) {
  return api.get(`/conversations/${corpusId}/style`)
}

// === 新增 Notes API ===
export function getNotes(corpusId) {
  return api.get(`/notes/${corpusId}`)
}
export function getNote(corpusId, noteId) {
  return api.get(`/notes/${corpusId}/${noteId}`)
}
export function generateNote(corpusId) {
  return api.post(`/notes/${corpusId}/generate`)
}
export function getLatestMindmap(corpusId) {
  return api.get(`/notes/${corpusId}/latest-mindmap`)
}

// === 新增 Skills API (v2) ===
export function exportSkillMarkdown(corpusId) {
  return api.get(`/skills/${corpusId}/export/markdown`)
}
export function exportSkillJson(corpusId) {
  return api.get(`/skills/${corpusId}/export/json`)
}
export function previewSkill(corpusId, format = 'markdown') {
  return api.get(`/skills/${corpusId}/preview`, { params: { format } })
}

// === 新增 Settings API ===
export function getSettings() {
  return api.get('/settings')
}
export function updateSettings(data) {
  return api.put('/settings', data)
}
export function getAvailableModels() {
  return api.get('/settings/models')
}
export function testConnection(data) {
  return api.post('/settings/test-connection', data)
}

// 网络搜索 provider
export function getSearchProviders() {
  return api.get('/settings/search/providers')
}
// QMD 推荐的嵌入/重排模型清单（下拉菜单数据源）
export function getSearchRagModels() {
  return api.get('/settings/search/rag-models')
}
export function testSearch(data) {
  return api.post('/settings/search/test', data, { timeout: 30000 })
}

// === 更新 Corpus API ===
export function getCorpusStatus(corpusId) {
  return api.get(`/corpus/${corpusId}/status`)
}
export function updateCorpus(corpusId, data) {
  return api.put(`/corpus/${corpusId}`, data)
}

export default api
