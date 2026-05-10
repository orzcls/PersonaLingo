# ALIGNMENT — 蒸馏链路三段式改造

## 1. 需求本源

用户要求:参考 `huashu-nuwa`(女娲造人)的 **"深度调研 → 思维框架提炼 → 生成可运行 Skill"** 三段式思想,审视 PersonaLingo 的核心功能「蒸馏学生定制专属语料库训练」,识别系统框架差距,并决定是否抽取其框架做深度适配。

## 2. 当前系统盘点(Sort — 剥离无用之前先看清楚有什么)

### 2.1 现有蒸馏链路(5 步)
位置:`backend/app/services/corpus_generator.py::CorpusGenerator.generate_full_corpus`

| 步骤 | 输入 | 产物 | 代码入口 |
|---|---|---|---|
| 1. Persona 用户画像 | MBTI + 兴趣 + 背景 | 画像字典 | `generate_persona()` |
| 2. Anchors 锚点故事 | Persona | 3-4 个故事 | `generate_anchors()` |
| 3. Bridges 题库桥接 | Anchors + Topics | 21 题桥接 | `generate_bridges()` |
| 4. Vocabulary 词汇升级 | Persona + 分数段 | 升级词表 | `generate_vocabulary()` |
| 5. Patterns 句型模板 | Persona + 分数段 | 句型包 | `generate_patterns()` |

### 2.2 现有入口
- 唯一入口:`POST /api/corpus/generate` 传 `questionnaire_id`,要求用户已完成完整 MBTI + 兴趣问卷

### 2.3 现有导出
- `skill_exporter.py` 导出 Markdown 摘要 / JSON 摘要
- 输出仅为锚点/词汇计数 + 流程说明,**非自包含可运行**

## 3. huashu-nuwa 框架要点

| 段 | 核心动作 | 关键产出 |
|---|---|---|
| 段1 深度调研 | 多源聚合背景/样本/领域知识 | 结构化调研档案 |
| 段2 框架提炼 | 从调研中抽象「思维/能力矩阵」 | 可复用的能力框架 |
| 段3 生成可运行 Skill | 把框架 + 数据打包成可被 Agent 独立加载运行的 Skill 包 | `.md` + `.json` + prompts + 调用协议 |
| 入口 | 明确目标直接蒸馏 / 模糊需求先诊断再蒸馏 | 双路分流 |

## 4. 差距识别

| 差距 | 现状 | 目标 |
|---|---|---|
| G1 调研深度 | 仅问卷输入 | 聚合 questionnaire + 对话历史 + 上传材料 + 题库信号 生成 `LearnerProfile` |
| G2 框架层缺失 | 从 Persona 直跳 Anchors | 插入「能力 × 场景 × 目标」三维 `CapabilityFramework` |
| G3 产物不可运行 | 仅摘要 | 导出自包含 Skill 包目录(md + corpus.json + runtime_protocol + prompts) |
| G4 入口单一 | 必须完成长问卷 | 新增模糊需求入口 → 诊断 → 生成建议问卷 |

## 5. 任务范围(Sort — 明确边界)

### 范围内(MUST)
- 新增 `learner_researcher.py`(Stage 1)
- 新增 `capability_framework.py`(Stage 2)
- 改造 `corpus_generator.py` 在 Stage 3 前串联 1+2
- 改造 `skill_exporter.py` 新增可运行包导出
- 新增路由 `distill.py` 暴露 3 个端点
- 扩展 `corpora` 表两个 JSON 字段
- 每个新模块最小单测
- 同步 skill md / README

### 范围外(YAGNI)
- 不重写 RAG / QMD 引擎
- 不替换 LLM 适配层
- 不改前端视觉与路由
- 不引入新数据表(仅扩字段)
- 不做多用户/权限
- 不做 Research 层的网页抓取(默认关闭,作为未来可选)

## 6. 验收标准(用于 Approve / Assess)

| # | 验收项 | 判定方式 |
|---|---|---|
| A1 | 旧调用 `POST /api/corpus/generate` 无 breaking change | 手动回归;corpus 仍可生成 |
| A2 | 新链路中 `learner_profile` / `capability_framework` 被持久化且可在 `GET /api/corpus/{id}` 返回 | 接口响应包含新字段 |
| A3 | `GET /api/distill/skill/{id}/runnable` 可下载到目录并包含 4 个产物 | 目录存在 + 文件齐全 |
| A4 | `POST /api/distill/diagnose` 给定模糊文本可返回诊断问卷 | 响应含 questions[] |
| A5 | 新模块单测全部 pass | `pytest` 绿 |
| A6 | `skills/personalingo_skill.md` 链路描述已更新到 7 步 | 文件对照 |

## 7. 开放项(交 Approve 阶段裁定)
- O1:Research 层是否默认调用 `web_search`?
- O2:Skill 包持久化路径是否为 `PersonaLingo/skills/runnable/{corpus_id}/`?

## 8. 默认决策(若用户未进一步指定)
- O1 默认 **关闭**,通过 `.env` 开关 `DISTILL_RESEARCH_WEB_SEARCH=false` 启用
- O2 默认 `PersonaLingo/skills/runnable/{corpus_id}/`
