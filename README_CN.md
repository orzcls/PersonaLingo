# PersonaLingo 个性化雅思口语语料库生成器

> 基于 MBTI 性格分析的 AI 驱动雅思口语语料库生成系统，支持 Agent Skill 导出

## 项目定位

PersonaLingo 将你的性格特征（MBTI）、兴趣爱好和雅思目标转化为量身定制的口语语料库——包含锚点故事、话题桥接、词汇升级和句式模板。并可将整个工作流导出为可复用的 AI Agent Skill。

## 核心功能

- **MBTI 驱动个性化** — 12题快速评估或直接选择性格类型
- **智能锚点策略** — 生成 3-4 个可桥接 20+ 雅思话题的个人故事
- **词汇与句式引擎** — 基于兴趣领域的高级词汇替换和句式升级
- **Agent Skill 导出** — 将工作流打包为 Trae/Cursor/GPTs/Coze/Dify 可用的 Skill
- **多格式导出** — Markdown、JSON Schema、OpenAPI 规范

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3, Vite, Tailwind CSS, Pinia |
| 后端 | FastAPI, Pydantic, OpenAI SDK |
| 大模型 | GPT-4o / GLM-4（可配置） |
| 导出 | Markdown, JSON Schema, OpenAPI 3.0 |

## 快速启动

### 后端
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入 API Key
python run.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

### Docker 一键启动
```bash
docker-compose up --build
```

访问 `http://localhost:5173` 开始使用。

## 为什么做这个项目

1. **解决真实痛点** — 雅思口语备考缺乏个性化语料，通用模板难以展现个人特色
2. **AI Agent 生态** — 将传统工具升级为可被 AI Agent 调用的 Skill，探索 LLM 应用新范式
3. **全栈工程实践** — 前后端分离架构 + LLM 集成 + Docker 部署的完整工程链路

## 许可证

MIT License
