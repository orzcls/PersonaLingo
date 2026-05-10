---
name: PersonaLingo
description: 个性化雅思口语语料生成器。纯 Agent 内闭环（问卷 → 引导对话 → 7 步蒸馏 → 个人画像 → 静态语料网站），零后端依赖，一键安装可用。需要题库自动同步 / RAG 检索可升级到 runnable-export 模式。
version: 3.1.0
entry: SKILL.md
mode: install-only
---

# PersonaLingo Skill · Install-only

> 一键安装，零后端依赖。Agent 在本地完成「问卷 → 引导对话 → 蒸馏画像 → 个人资料 → 静态语料网站」全链路。

## Installation

```bash
npx skills add orzcls/PersonaLingo
```

安装产物（由 `skill.json` 的 `files` 白名单约束）：

```
.agents/skills/personalingo/
├── SKILL.md
├── skill.json
└── skill-assets/
    ├── questionnaire.json          # 问卷 Schema
    ├── conversation-guide.md       # 引导对话规则
    ├── distill-protocol.md         # 7 步蒸馏 prompt 协议
    ├── corpus-schema.json          # corpus.json 校验 schema（与后端 models/corpus.py 等价）
    ├── profile-template.md         # 个人资料模板
    ├── site-template.html          # 静态网站模板
    ├── band-strategies.json        # 分数段策略（与后端 band_strategies.json 一致）
    ├── fallback-topics.json        # Stage 5 降级题库（20 话题）
    ├── fallback-vocabulary.json    # Stage 6 降级词表（按 band 分档）
    └── fallback-patterns.json      # Stage 7 降级句型（8 条通用模板）
```

不会再复制 `backend/` / `frontend/` / `docs/` 等项目代码。

## 运行时目录

Agent 每次为新学习者创建独立工作区：

```
corpus/<corpus_id>/
├── answers.json        # Step 1 问卷作答
├── dialogue.md         # Step 2 引导对话日志
├── corpus.json         # Step 3 蒸馏产物（符合 corpus-schema.json）
├── profile.md          # Step 4 个人资料
└── site/
    └── index.html      # Step 5 静态语料网站
```

`<corpus_id>` 建议用 `p_` + 8 位十六进制随机数（例：`p_0a1b2c3d`）。

## Pipeline · 五步闭环

### Step 1 · 问卷（Questionnaire）

1. 读取 [skill-assets/questionnaire.json](skill-assets/questionnaire.json)。
2. 按 `ask_order: sequential`、`sections[].questions[]` 的顺序逐题询问用户。
3. `required: true` 的题目必须得到作答；其它题可由用户跳过（值写 `null`）。
4. 所有作答合并为：

   ```json
   {
     "corpus_id": "p_0a1b2c3d",
     "created_at": "2026-05-11T10:00:00Z",
     "answers": {
       "goal": { "target_band": "7.0", "exam_window": "1-3 个月", "current_band": "6.0" },
       "persona": { "mbti": "INTJ", "communication_style": ["逻辑结构化"], "self_description": "..." },
       "experiences": { "people": [...], "objects": [...], "places": [...], "events": [...] },
       "interests": { "interests": ["科技/编程"], "expertise": "..." },
       "weaknesses": { "weak_areas": ["句型单一"], "recurring_mistakes": "..." }
     }
   }
   ```

5. 写入 `corpus/<corpus_id>/answers.json`。

### Step 2 · 引导对话（Guided Conversation）

1. 读取 [skill-assets/conversation-guide.md](skill-assets/conversation-guide.md)。
2. 按"追问原则"与"追问模板"发起 3–6 轮对话，每轮仅一个聚焦问题。
3. 记录每轮对话到 `corpus/<corpus_id>/dialogue.md`（Markdown 格式，含时间戳）。
4. 达到"结束条件"时在文件末追加 `Summary`（锚点事件 / 语言样本 / 弱项证据）。

### Step 3 · 七步蒸馏（Distill）

1. 加载 [skill-assets/distill-protocol.md](skill-assets/distill-protocol.md) 与 [skill-assets/band-strategies.json](skill-assets/band-strategies.json)。
2. 从 `answers.json` 读取 `target_band`，取出对应分数档策略块（若 `8.0+ / 暂不考试` → 兜底用 `7.5`）。
3. 串行执行 7 个 Stage 的 LLM Prompt，**Stage 3-7 的 system prompt 必须注入 band_strategy 块**（与后端 `corpus_generator.py` 等价）：
   - `research`   → `learner_profile`（background / goal_vector / weakness_signals / language_samples / topic_signals / source_stats）
   - `framework`  → `capability_framework`（source / dimensions / pain_points / lift_paths）
   - `persona`    → `persona`（mbti / dimensions / communication_style）
   - `anchors`    → `anchors[]`
   - `bridges`    → `bridges[]`
   - `vocabulary` → `vocabulary[]`
   - `patterns`   → `patterns[]`
4. 任一 Stage 失败按 protocol 的「降级策略」处理：Agent 必须在 `skill_manifest.stages[i]` 写 `status="fallback"` + `source` + `note`，并依次调用对应 fallback 资产：
   - Stage 5 降级 → `skill-assets/fallback-topics.json`
   - Stage 6 降级 → `skill-assets/fallback-vocabulary.json`（按 `target_band ± 0.5` 筛选）
   - Stage 7 降级 → `skill-assets/fallback-patterns.json`
5. 合并写入 `corpus/<corpus_id>/corpus.json`，**必须通过** [skill-assets/corpus-schema.json](skill-assets/corpus-schema.json) 的 JSON Schema 校验。
6. 将实际使用的 band 策略快照写入 `corpus.band_strategy`，供下游追溯。

### Step 4 · 个人资料（Profile）

1. 读取 [skill-assets/profile-template.md](skill-assets/profile-template.md)。
2. 用 `corpus.json` 的字段替换 `{{ ... }}` 占位符；数组字段按 `{{#each}}` 循环展开；缺失字段输出 `—`。
3. 写入 `corpus/<corpus_id>/profile.md`。

### Step 5 · 静态语料网站（Static Site）

1. 读取 [skill-assets/site-template.html](skill-assets/site-template.html)。
2. 同样用 `corpus.json` 字段填充模板，生成单文件 HTML（所有样式 inline，无构建依赖）。
3. 写入 `corpus/<corpus_id>/site/index.html`。
4. 用户直接 `open site/index.html` 即可浏览个人语料站点。

## 质量守则

- **真实性优先**：锚点故事、词汇例句必须来自问卷 + 对话的真实素材，禁止虚构。
- **架构等价**：install-only 产出的 `corpus.json` 必须与 runnable-export 同 schema（见 `skill.json.install_only.schema_alignment`），下游 Agent 可用统一逻辑读两种模式的结果。
- **Schema 严格**：`corpus.json` 必须通过 `corpus-schema.json` 校验；不符字段直接丢弃并在 `stages[i].note` 记录原因。
- **Band 注入**：Stage 3-7 没有注入 band_strategy 等于没在蒸馏——产物会偏离目标分数档。
- **本地化**：所有产物写到当前工作目录的 `corpus/<corpus_id>/`，不上传任何远程服务。
- **可复跑**：每一步都以前序产物为唯一输入；任何一步可单独重跑而不影响其它步骤。

## 升级路径 — Runnable Export 模式

若学习者需要以下能力，建议升级到完整 orzcls/PersonaLingo 项目：

| 能力 | Install-only | Runnable Export |
|---|---|---|
| 问卷 / 对话 / 蒸馏 | Agent 内闭环 | 后端 API 驱动 + 前端 UI |
| 动态 IELTS 题库同步 | 否 | 支持季度自动同步 |
| QMD RAG 检索引擎 | 否 | BM25+TF-IDF+RRF+LLM 重排 |
| 对话风格学习持久化 | 否（单次会话） | SQLite 持久化 |
| 可运行 Skill 包导出 | 否（本地产物可手动打包） | `/api/distill/skill/{id}/runnable/download` |

升级方式：

```bash
git clone https://github.com/orzcls/PersonaLingo
cd PersonaLingo && docker-compose up -d
# 访问 http://localhost:5273 使用完整前端
```

详见项目 [README.md](https://github.com/orzcls/PersonaLingo/blob/main/README.md)。

## Requirements

- 任意支持该 skill 协议的 AI Agent（Claude / Qoder / Cursor / Cline 等）。
- Agent 运行环境中可写本地文件的工具（用于产出 `corpus/<corpus_id>/`）。
- 无需 Python / Node.js / 任何外部服务。
