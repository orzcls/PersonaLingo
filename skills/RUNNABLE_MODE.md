# PersonaLingo · Runnable Export Mode

> 本文档只覆盖 **Mode 2 · Runnable Export**（后端驱动、导出可运行技能包）。
> 若你要的是一键装到 Agent 且零后端依赖的版本，请看仓库根 [SKILL.md](../SKILL.md)（Install-only 模式）。

Runnable Export 模式的定位：用本仓库的 backend + frontend 跑完整蒸馏流程，产出**持久化**、**QMD RAG 可检索**、**可下载 zip** 的技能包；适合辅导平台 / 长期学员 / 多轮风格学习场景。

## 1. 前置条件

- 已按 [README.md · Quick Start](../README.md#quick-start) 跑起后端（默认 `http://localhost:9849`）。
- 已配置 LLM Key（OpenAI / Anthropic 其一）。
- 可选：配置搜索 Key 以启用动态题库同步。

## 2. 导出产物结构

每个 `corpus_id` 独立输出到：

```
skills/runnable/<corpus_id>/
├── Skill.md              # 个性化学习 skill 文档
├── corpus.json           # 完整语料 + learner_profile + capability_framework + QMD 标签
├── runtime_protocol.md   # Agent 运行时协议（RAG 检索 / 生成响应）
└── prompts/
    └── README.md         # 对话与测评 prompt 模板
```

`corpus.json.skill_manifest.mode = "runnable-export"`；schema 与 Install-only 模式共用 `skill-assets/corpus-schema.json`。

## 3. API 调用序列

### Step 1 — 诊断问卷

```bash
curl -X POST http://localhost:9849/api/distill/diagnose \
  -H "Content-Type: application/json" \
  -d '{"text": "I am an INTJ aviation student aiming at 7.0 speaking but weak in fluency."}'
```

响应中返回 `questions[]` 与 `suggested_score`，前端渲染作答后取得 `questionnaire_id`。

### Step 2（可选） — 引导对话补充

```bash
curl -X POST http://localhost:9849/api/conversation/{corpus_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I competed in ICPC 2024 regional and we scraped into the finals."}'
```

所有对话经 `/api/conversation/{corpus_id}/extract` + `/merge` 后沉淀进 corpus。

### Step 3 — 触发 7 步蒸馏

```bash
curl -X POST "http://localhost:9849/api/distill/run?questionnaire_id={id}&include_research=true"
```

返回 `stream_url`，可用 SSE 订阅各 Stage 进度：
`research → framework → persona → anchors → bridges → vocabulary → patterns`。Stage 1/2 失败会自动降级到 5 步旧流程。

### Step 4 — 列出 / 预览 / 下载 Skill Pack

```bash
# 列文件
curl http://localhost:9849/api/distill/skill/{corpus_id}/runnable

# 在线预览 Skill.md
curl "http://localhost:9849/api/distill/skill/{corpus_id}/runnable/preview?format=markdown"

# 打包下载
curl http://localhost:9849/api/distill/skill/{corpus_id}/runnable/download -o personalingo_{corpus_id}.zip
```

## 4. 下游 Agent 加载

1. 解压 zip 到 agent 的 skills 目录。
2. 读取 `corpus.json` 获得完整 profile / framework / anchors / bridges / vocabulary / patterns。
3. 按 `runtime_protocol.md` 执行 RAG 检索 / 回复生成。
4. 需要再次蒸馏时回调 `POST /api/distill/run?questionnaire_id=<id>`。

## 5. 与 Install-only 模式的区别

| 维度 | Install-only | Runnable Export |
|---|---|---|
| 入口 | `npx skills add orzcls/PersonaLingo` | `git clone` + `docker-compose up` |
| 存储 | Agent 本地文件系统 | SQLite + 后端服务 |
| 检索 | 无（Agent prompt 内展开） | QMD RAG（BM25 + TF-IDF + RRF + LLM 重排） |
| 题库 | 不同步 | 季度自动同步 P1/P2，反向回填 P3 |
| 产物 | 5 件套（含静态网站） | 4 件套（Skill.md / corpus.json / runtime_protocol.md / prompts/） |
| 适用 | 单次个性化、即插即用 | 长期辅导、多轮持久化 |

## 6. 已导出示例

本仓库内置的示例包位于 `skills/runnable/`：

- `skills/runnable/smoke_c_0a0e63e4/`
- `skills/runnable/smoke_c_0fe070a1/`

可作为集成测试样本或自定义 agent 的参考输入。
