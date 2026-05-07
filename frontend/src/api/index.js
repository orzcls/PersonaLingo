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

// 获取 Skill 格式列表
export function getSkillFormats() {
  return api.get('/skill/formats')
}

// 导出 Skill
export function exportSkill(format, corpusId) {
  return api.post('/skill/export', { format, corpus_id: corpusId })
}

export default api
