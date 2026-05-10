import { reactive, computed } from 'vue'

const messages = {
  zh: {
    // 导航
    nav: {
      home: '首页',
      questionnaire: '问卷',
      topics: '题库',
      corpus: '语料库',
      chat: '对话',
      notes: '笔记',
      export: '导出',
      settings: '设置'
    },
    // 首页
    home: {
      title: 'PersonaLingo',
      subtitle: 'AI 驱动的个性化雅思口语语料库生成系统',
      slogan: '你的性格，你的故事，你的语料库。—— 说自己的话，拿理想的分。',
      cta: '开始生成你的专属语料库',
      featuresTitle: '核心功能',
      features: {
        corpus: { title: '智能语料生成', desc: 'MBTI+兴趣问卷→5步AI生成个性化语料库' },
        topics: { title: '动态题库管理', desc: 'P1/P2/P3题库浏览、按季度/类别筛选、一键导入' },
        chat: { title: '对话维护', desc: 'NotebookLM风格聊天，AI教练帮你维护和更新语料' },
        rag: { title: 'RAG 智能检索', desc: '内置QMD引擎，对话中自动引用相关语料' },
        notes: { title: '学习笔记', desc: '每次训练/维护后自动生成摘要和思维导图' },
        band: { title: '分数段策略', desc: '6.0/6.5/7.0/7.5+ 四级差异化输出' }
      }
    },
    // 题库
    topics: {
      title: '题库管理',
      subtitle: '浏览和管理雅思口语话题',
      search: '搜索话题...',
      total: '总计',
      newTopics: '新题',
      uploadBtn: '上传题库',
      scrapeBtn: '获取最新题库',
      scrapeBtnSeason: '刷新 {season} 题库',
      scraping: '抓取中…',
      currentSeason: '当前考试季',
      lastUpdated: '上次更新',
      staleHint: '可能不是最新考试季，建议刷新',
      sources: '来源',
      scrapeSuccess: '已刷新 {season}：P1 新增 {p1} · P2 新增 {p2} · P3 新增 {p3}（其中衍生 {derived}）· 更新 {updated} 条',
      scrapeEmpty: '未抓取到新题，可能来源受限或全部已存在。',
      scrapeFail: '获取失败：',
      configMissing: '未配置 LLM 或搜索服务，正在跳转到设置页…',
      all: '全部',
      filterPart: 'Part',
      filterSeason: '季度',
      filterCategory: '类别',
      difficulty: '难度',
      questions: '问题',
      startPractice: '开始练习',
      recommendedAnchors: '推荐锚点',
      showing: '显示',
      topicsCount: '个话题',
      emptyTitle: '没有找到匹配的话题',
      emptyHint: '尝试调整搜索条件或筛选器',
      loading: '正在加载话题...',
      uploadSuccess: '上传成功！导入 {imported} 题，跳过 {skipped} 题（重复）',
      uploadFail: '上传失败：',
      uploading: '正在上传 {name}...'
    },
    // 对话
    chat: {
      title: '语料库对话维护',
      subtitle: '与AI教练对话，维护和更新你的语料库',
      corpusId: '语料库 ID',
      notLinked: '未关联',
      inputPlaceholder: '输入消息，与AI教练对话...',
      send: '发送',
      emptyState: '开始与AI教练对话',
      emptyHint: '你可以分享新的经历、练习回答、或请求更新语料库',
      extractor: '语料提取器',
      merge: '融合到语料库',
      anchors: '锚点',
      vocabulary: '词汇',
      bridges: '桥接',
      patterns: '句型'
    },
    // 笔记
    notes: {
      title: '学习笔记',
      subtitle: '每次训练和维护后自动生成的学习记录',
      empty: '暂无笔记',
      emptyHint: '完成语料库生成或对话维护后将自动生成笔记',
      generateBtn: '手动生成',
      changes: '变更记录',
      tips: '学习建议',
      mindmap: '思维导图',
      backToNotes: '返回笔记列表'
    },
    // 设置
    settings: {
      title: '设置',
      subtitle: '配置LLM提供商和系统偏好',
      provider: 'LLM 提供商',
      providerDesc: '选择你偏好的AI提供商用于语料生成',
      baseUrl: '请求地址',
      baseUrlHint: '支持任何 OpenAI-compatible API 地址',
      baseUrlHintAnthropic: 'Anthropic API 请求地址',
      apiKey: 'API 密钥',
      model: '模型选择',
      refreshModels: '刷新',
      testConnection: '测试连接',
      testConnectionTitle: '连接测试',
      testConnectionDesc: '测试你的 API 连接',
      targetScore: '目标雅思分数',
      targetScoreDesc: '选择你的目标分数以获得个性化难度',
      language: '界面语言',
      save: '保存设置',
      saving: '保存中...',
      saveSuccess: '设置保存成功！',
      saveFail: '保存设置失败，请重试。',
      connected: '已连接 — 准备就绪',
      notConfigured: '未配置 — 请设置你的 API 密钥',
      noModels: '未获取到模型列表，请检查 Base URL 和 API Key',
      modelFetchFail: '获取模型列表失败: ',
      webSearch: {
        title: '网络搜索',
        subtitle: '用于动态抓取雅思题库来源',
        apiProviders: 'API 服务商',
        localProviders: '本地搜索',
        apiKey: 'API 密钥',
        baseUrl: '请求地址（可选）',
        general: '常规设置',
        includeDate: '搜索结果包含日期',
        maxResults: '搜索结果个数',
        compression: '搜索结果压缩',
        compressMethod: '压缩方法',
        chunkCount: '文档片段数量',
        compressOptions: {
          rag: 'RAG (BM25+TF-IDF)',
          truncate: '截断',
          none: '不压缩'
        },
        test: '测试搜索',
        testing: '测试中…',
        testOk: '搜索可用，耗时 {ms}ms，返回 {n} 条',
        testFail: '搜索失败：',
        groupApi: 'API 服务',
        groupLocal: '本地抓取',
        loadingProviders: '正在加载搜索服务商…（如持续空白请检查后端 /api/settings/search/providers）',
        embeddingModel: '嵌入模型',
        embeddingModelPh: '如 text-embedding-3-small / bge-m3（留空走本地 BM25）',
        embeddingModelHint: 'QMD 已自动检测可用模型，下拉选择即可；选「自定义」可手动填写。',
        embeddingDim: '嵌入维度',
        embeddingDimHint: '选定预设后维度已自动填好；0 表示自动探测。',
        rerankerModel: '重排模型',
        rerankerModelPh: '如 bge-reranker-v2-m3（留空不重排）',
        rerankerModelHint: 'QMD D 层默认用 LLM 重排；选外部重排模型可进一步提升命中质量。',
        ragPresetAuto: '自动检测 QMD 模型中…',
        ragPresetCustom: '自定义模型 ID',
        ragPresetLoadFail: '预设加载失败，已降级为手动输入'
      }
    },
    // 导出
    export: {
      title: '导出语料库与Skill',
      subtitle: '下载你的个性化语料库或导出可复用的AI Agent Skill文件',
      downloadCorpus: '下载语料库',
      htmlFile: 'HTML 文件',
      htmlDesc: '独立HTML页面 — 在任何浏览器中打开，离线可用',
      jsonData: 'JSON 数据',
      jsonDesc: '原始结构化数据 — 适合程序化使用或进一步处理',
      downloadHtml: '下载 .html',
      downloadJson: '下载 .json',
      skillExport: '导出 AI Agent Skill',
      skillExportDesc: '将整个问卷→语料生成工作流打包为可复用的Skill文件',
      preview: '预览',
      download: '下载',
      usageGuide: '如何使用导出的Skill',
      traeDesc: '将 .md 文件放入项目的 .trae/skills/ 或规则目录中，Agent会自动发现和使用它。',
      gptsDesc: '上传 .json 文件作为skill定义，或粘贴到你的Agent配置面板中。',
      apiDesc: '导入 .yaml OpenAPI规范，Agent可以直接调用 PersonaLingo API。',
      copyToClipboard: '复制到剪贴板',
      copied: '已复制！',
      viewSource: '在 GitHub 上查看源码 →'
    },
    // 语料库
    corpus: {
      title: '你的个性化语料库',
      subtitle: 'AI生成的雅思口语素材，专为你的性格和兴趣定制',
      chatBtn: '对话维护',
      uploadBtn: '上传资料',
      downloadHtml: '下载 HTML',
      exportSkill: '导出 Skill',
      generateNew: '重新生成',
      loading: '正在加载你的语料库...',
      errorTitle: '加载语料库失败',
      retry: '重试'
    },
    // 通用
    common: {
      loading: '加载中...',
      error: '出错了',
      retry: '重试',
      cancel: '取消',
      confirm: '确认',
      save: '保存',
      delete: '删除',
      edit: '编辑',
      close: '关闭'
    },
    // 页脚
    footer: {
      copyright: '© 2026 PersonaLingo. AI驱动的个性化雅思口语语料库生成系统。'
    }
  },
  en: {
    nav: {
      home: 'Home',
      questionnaire: 'Questionnaire',
      topics: 'Topics',
      corpus: 'Corpus',
      chat: 'Chat',
      notes: 'Notes',
      export: 'Export',
      settings: 'Settings'
    },
    home: {
      title: 'PersonaLingo',
      subtitle: 'AI-Powered Personalized IELTS Speaking Corpus Generator',
      slogan: 'Your personality. Your stories. Your corpus. — Speak like yourself, score like a pro.',
      cta: 'Start Generating Your Corpus',
      featuresTitle: 'Core Features',
      features: {
        corpus: { title: 'Smart Corpus Generation', desc: 'MBTI + interests → 5-step AI-powered personalized corpus' },
        topics: { title: 'Dynamic Topic Bank', desc: 'P1/P2/P3 topics with season/category filtering & import' },
        chat: { title: 'Chat Maintenance', desc: 'NotebookLM-style chat with AI coach to maintain your corpus' },
        rag: { title: 'RAG Smart Search', desc: 'Built-in QMD engine for context-aware conversations' },
        notes: { title: 'Learning Notes', desc: 'Auto-generated summaries & mind maps after each session' },
        band: { title: 'Band Strategies', desc: 'Differentiated output for 6.0/6.5/7.0/7.5+ targets' }
      }
    },
    topics: {
      title: 'Topic Bank',
      subtitle: 'Browse and manage IELTS speaking topics',
      search: 'Search topics by title...',
      total: 'Total',
      newTopics: 'New',
      uploadBtn: 'Upload Topics',
      scrapeBtn: 'Fetch Latest',
      scrapeBtnSeason: 'Refresh {season} bank',
      scraping: 'Scraping…',
      currentSeason: 'Current season',
      lastUpdated: 'Updated',
      staleHint: 'Season looks stale — refresh recommended',
      sources: 'Sources',
      scrapeSuccess: 'Refreshed {season}: +{p1} P1 · +{p2} P2 · +{p3} P3 (derived {derived}) · updated {updated}',
      scrapeEmpty: 'No new topics fetched. Source blocked or all already exist.',
      scrapeFail: 'Fetch failed: ',
      configMissing: 'LLM or search provider not configured. Redirecting to Settings…',
      all: 'All',
      filterPart: 'Part',
      filterSeason: 'Season',
      filterCategory: 'Category',
      difficulty: 'Difficulty',
      questions: 'Questions',
      startPractice: 'Start Practice',
      recommendedAnchors: 'Recommended Anchors',
      showing: 'Showing',
      topicsCount: 'topics',
      emptyTitle: 'No topics found matching your filters',
      emptyHint: 'Try adjusting your search or filter criteria',
      loading: 'Loading topics...',
      uploadSuccess: 'Upload successful! Imported {imported}, skipped {skipped} (duplicate)',
      uploadFail: 'Upload failed: ',
      uploading: 'Uploading {name}...'
    },
    chat: {
      title: 'Corpus Chat Maintenance',
      subtitle: 'Chat with AI coach to maintain and update your corpus',
      corpusId: 'Corpus ID',
      notLinked: 'Not linked',
      inputPlaceholder: 'Type a message to chat with AI coach...',
      send: 'Send',
      emptyState: 'Start a Conversation',
      emptyHint: 'Chat with AI to refine and expand your IELTS speaking corpus. Ask questions, practice responses, or request new vocabulary.',
      extractor: 'Extractor',
      merge: 'Merge to Corpus',
      anchors: 'Anchors',
      vocabulary: 'Vocabulary',
      bridges: 'Bridges',
      patterns: 'Patterns'
    },
    notes: {
      title: 'Learning Notes',
      subtitle: 'Auto-generated records after each training and maintenance session',
      empty: 'No notes yet',
      emptyHint: 'Notes will be auto-generated after corpus generation or chat maintenance',
      generateBtn: 'Generate Manually',
      changes: 'Changes & Improvements',
      tips: 'Tips & Suggestions',
      mindmap: 'Mind Map',
      backToNotes: 'Back to notes'
    },
    settings: {
      title: 'Settings',
      subtitle: 'Configure LLM provider and system preferences',
      provider: 'LLM Provider',
      providerDesc: 'Choose your preferred AI provider for corpus generation',
      baseUrl: 'Base URL',
      baseUrlHint: 'Supports any OpenAI-compatible API endpoint',
      baseUrlHintAnthropic: 'Anthropic API endpoint',
      apiKey: 'API Key',
      model: 'Model',
      refreshModels: 'Refresh',
      testConnection: 'Test Connection',
      testConnectionTitle: 'Connection Test',
      testConnectionDesc: 'Test your API connection',
      targetScore: 'Target IELTS Score',
      targetScoreDesc: 'Select your target band score for personalized difficulty',
      language: 'Interface Language',
      save: 'Save Settings',
      saving: 'Saving...',
      saveSuccess: 'Settings saved successfully!',
      saveFail: 'Failed to save settings. Please try again.',
      connected: 'Connected — Ready to use',
      notConfigured: 'Not configured — Please set up your API key',
      noModels: 'No models found. Please check Base URL and API Key',
      modelFetchFail: 'Failed to fetch models: ',
      webSearch: {
        title: 'Web Search',
        subtitle: 'Used to fetch fresh IELTS topic sources',
        apiProviders: 'API Providers',
        localProviders: 'Local Providers',
        apiKey: 'API Key',
        baseUrl: 'Base URL (optional)',
        general: 'General',
        includeDate: 'Include date in search results',
        maxResults: 'Max result count',
        compression: 'Result Compression',
        compressMethod: 'Compression Method',
        chunkCount: 'Chunk count',
        compressOptions: {
          rag: 'RAG (BM25+TF-IDF)',
          truncate: 'Truncate',
          none: 'None'
        },
        test: 'Test Search',
        testing: 'Testing…',
        testOk: 'Search OK in {ms}ms, {n} results',
        testFail: 'Search failed: ',
        groupApi: 'API providers',
        groupLocal: 'Local scrapers',
        loadingProviders: 'Loading providers… (empty means backend /api/settings/search/providers is unreachable)',
        embeddingModel: 'Embedding model',
        embeddingModelPh: 'e.g. text-embedding-3-small / bge-m3 (empty = local BM25)',
        embeddingModelHint: 'QMD auto-detected presets — just pick one. Choose Custom to type your own.',
        embeddingDim: 'Embedding dimension',
        embeddingDimHint: 'Auto-filled when a preset is selected; 0 = auto-detect.',
        rerankerModel: 'Reranker model',
        rerankerModelPh: 'e.g. bge-reranker-v2-m3 (empty = no rerank)',
        rerankerModelHint: 'QMD D-layer already uses LLM rerank; external reranker can further boost precision.',
        ragPresetAuto: 'Auto-detecting QMD models…',
        ragPresetCustom: 'Custom model ID',
        ragPresetLoadFail: 'Preset load failed — falling back to manual input'
      }
    },
    export: {
      title: 'Export Your Corpus & Skills',
      subtitle: 'Download your personalized corpus or export reusable AI Agent Skill files for any platform.',
      downloadCorpus: 'Download Corpus',
      htmlFile: 'HTML File',
      htmlDesc: 'Standalone HTML page — open in any browser, works offline.',
      jsonData: 'JSON Data',
      jsonDesc: 'Raw structured data — ideal for programmatic use or further processing.',
      downloadHtml: 'Download .html',
      downloadJson: 'Download .json',
      skillExport: 'Export AI Agent Skill',
      skillExportDesc: 'Package the entire questionnaire → corpus generation workflow as a reusable Skill file for any AI Agent platform.',
      preview: 'Preview',
      download: 'Download',
      usageGuide: 'How to Use Exported Skills',
      traeDesc: 'Place the .md file in your project\'s .trae/skills/ or rules directory. The agent will automatically discover and use it.',
      gptsDesc: 'Upload the .json file as a skill definition or paste it into your agent\'s configuration panel.',
      apiDesc: 'Import the .yaml OpenAPI spec. The agent can call PersonaLingo APIs directly.',
      copyToClipboard: 'Copy to Clipboard',
      copied: 'Copied!',
      viewSource: 'View source on GitHub →'
    },
    corpus: {
      title: 'Your Personalized Corpus',
      subtitle: 'AI-generated IELTS speaking materials tailored to your personality and interests',
      chatBtn: 'Chat Maintenance',
      uploadBtn: 'Upload Material',
      downloadHtml: 'Download HTML',
      exportSkill: 'Export as Skill',
      generateNew: 'Generate New',
      loading: 'Loading your corpus...',
      errorTitle: 'Failed to load corpus',
      retry: 'Retry'
    },
    common: {
      loading: 'Loading...',
      error: 'Error',
      retry: 'Retry',
      cancel: 'Cancel',
      confirm: 'Confirm',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      close: 'Close'
    },
    footer: {
      copyright: '© 2026 PersonaLingo. AI-Powered Personalized IELTS Speaking Corpus Generator.'
    }
  }
}

// 当前语言状态
const state = reactive({
  locale: localStorage.getItem('locale') || 'zh'
})

// 获取翻译函数
export function useI18n() {
  const t = (key) => {
    const keys = key.split('.')
    let result = messages[state.locale]
    for (const k of keys) {
      result = result?.[k]
    }
    return result || key
  }

  const locale = computed(() => state.locale)

  const setLocale = (lang) => {
    state.locale = lang
    localStorage.setItem('locale', lang)
  }

  return { t, locale, setLocale }
}

export default { messages, state }
