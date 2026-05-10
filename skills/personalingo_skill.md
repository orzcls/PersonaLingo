# PersonaLingo Skill - [MBTI_TYPE]

## 语料库生成流程（三段式蒸馏 · v3.0）

> **v3.0 升级说明**：借鉴 `huashu-nuwa` 的「深度调研→思维框架→可运行 Skill」三段式，对蒸馏链路做前置增强。原 5 步（Persona→Anchors→Bridges→Vocabulary→Patterns）前置两步（Research→Framework）扩展为 **7 步链路**，并新增「可运行 Skill 包」作为第三段交付物。Stage 1/2 失败时自动降级到 5 步流程，向后兼容。

### 输入
- MBTI 类型 + 兴趣问卷 + 目标分数（+ 可选：上传资料、历史对话、主题信号）

### 流程（7 步）
0. **深度调研 (Stage 1 · Research)** → 聚合问卷/资料/对话/主题 → 产出 `learner_profile`（background / language_samples / weakness_signals / goal_vector / topic_signals）
1. **思维框架提炼 (Stage 2 · Framework)** → LLM 对 profile 做三维矩阵蒸馏（ability × scenario × goal）→ 产出 `capability_framework`（含 pain_points / lift_paths），LLM 失败自动规则兜底
2. **用户画像生成 (Stage 3a · Persona)** → MBTI 维度分析 + 沟通风格推断
3. **锚点故事生成 (Stage 3b · Anchors)** → 3-4 个个人核心故事
4. **题库桥接 (Stage 3c · Bridges)** → 21 题桥接法连接锚点与题库
5. **词汇升级 (Stage 3d · Vocabulary)** → 分数段适配的词汇表
6. **句型模板 (Stage 3e · Patterns)** → MBTI 匹配的表达模式

### 输出
- 完整个性化语料库（含 `learner_profile` + `capability_framework`）
- 可运行 Skill 包（4 件套：`Skill.md` + `corpus.json` + `runtime_protocol.md` + `prompts/README.md`）

### 面向外部 Agent（可运行 Skill 调用协议）
当 Agent 被要求「加载 PersonaLingo 学习者画像并进行口语陪练」时：
```
Input:
  - corpus_id (str)
  - optional: out_root (用于落盘的目录)

Step 1. 调用 POST /api/distill/run?questionnaire_id=Q&include_research=true
        → 后台串联 7 步，learner_profile/capability_framework 落 DB
Step 2. 调用 GET  /api/distill/skill/{corpus_id}/runnable
        → 服务侧产出 4 件套到 SKILL_RUNNABLE_OUT_ROOT/{corpus_id}/
Step 3. （可选）GET /api/distill/skill/{corpus_id}/runnable/download 拉取 zip
Step 4. Agent 加载 corpus.json.skill_manifest：
        { name, version, pipeline="three_stage_distill",
          stages=[research,framework,persona,anchors,bridges,vocabulary,patterns] }
        按 runtime_protocol.md 指引调用 prompts/ 下模板
Fallback:
  - Stage 1/2 失败不阻断 Stage 3；corpus_manifest 标记 stages.*.status=skipped
  - LLM 均不可用时 capability_framework 走规则兜底（非空）
```

### 相关 API 速查（三段式蒸馏）
| 端点 | 作用 |
|------|------|
| `POST /api/distill/diagnose` | 诊断问卷生成（失败用 3 条默认问题兜底） |
| `POST /api/distill/run?questionnaire_id=&include_research=true` | 后台触发 7 步蒸馏 |
| `GET  /api/distill/skill/{corpus_id}/runnable` | 产出可运行 Skill 包 4 件套 |
| `GET  /api/distill/skill/{corpus_id}/runnable/download` | 打包 zip 流式下载 |

## 对话维护流程

### 输入
- 用户对话 / 上传资料

### 流程
1. **RAG 检索** → 从语料库获取相关上下文
2. **对话回复** → 带教练角色的智能回复
3. **内容提取** → 识别可加入语料库的新素材
4. **风格学习** → 更新用户表达风格统计
5. **语料融合** → 确认后更新语料库

### 输出
- 更新后的语料库 + 学习笔记

## 当前语料库摘要
- 锚点数: N
- 桥接数: N
- 词汇数: N
- 句型数: N
- 目标分数: X.X

## 用户风格特征
- MBTI类型: XXXX
- 平均句长: X words
- 常用连接词: ...
- 词汇层级: ...

## 锚点故事概览
- **锚点1**: keywords...
- **锚点2**: keywords...
- **锚点3**: keywords...

## Dynamic Topic Bank Update（动态题库更新）

> 本章节同时面向【普通用户】与【外部 Agent】，告知如何在考试季切换时刷新 IELTS 口语题库，保证 P1/P2/P3 覆盖最新真题。

### 面向普通用户（PersonaLingo 内使用）
1. 打开【设置】页 → 配置任一 LLM（OpenAI / Anthropic）并保存。
2. 在【网络搜索】卡片选择一个 provider：
   - API 类（需 Key）：Tavily / Exa / ExaMCP / Bocha / Zhipu / Querit / Searxng
   - 本地类（免 Key，通过 Jina Reader 抓取）：Google / Bing / Baidu
   - 点【测试搜索】确认连通。
3. 回到【题库】页：
   - 顶部显示“当前考试季 YYYY-QX · 上次更新 …”。若显示红点提示“可能不是最新考试季”，说明 DB 中的最新 season 滞后。
   - 点击【刷新 YYYY-QX 题库】按钮，系统会并行抓取多源 SERP → 构建临时 BM25+TF-IDF 索引 → LLM 严格从正文抽取 P1/P2 真题 → 对每道 P2 自动衍生 3-4 道 linked P3。
   - 完成后在状态条看到 “P1 新增 X · P2 新增 Y · P3 新增 Z（衍生 N）· 更新 K 条” 及前 3 个来源 URL。
4. 若想为历史 P2 补全 P3：调用 `POST /api/topics/backfill-p3?limit=20`（或在 DevTools 控制台执行）。

### 面向外部 Agent（标准执行协议）
当 Agent 被要求 “fetch latest IELTS season topics” 时，按以下协议执行：

#### 协议：IELTS_TOPIC_SYNC
```
Input:
  - current_date (ISO)
  - optional: parts ⊆ {P1, P2}   # P3 由 P2 衍生，不直接抓
  - required env: LLM API key, Search provider key

Step 1. 计算 season：quarter = (month-1)//4 + 1  → `YYYY-Q{1|2|3}`
Step 2. 为每个 part 构造 2-3 条 query：
        - "IELTS Speaking Part {n} topics {season} {year} new list"
        - "雅思口语 Part{n} {season} 新题 题库"
Step 3. 调用 PersonaLingo `POST /api/topics/scrape`（推荐）；
        或自行执行：
          3a. web_search(provider, query, max_results=20)
          3b. fetch 正文（优先 https://r.jina.ai/{url}，降级 httpx）
          3c. chunk_text(doc, 800, overlap=120) → 临时 BM25+TF-IDF 索引
          3d. retrieve_context(query, top_k=6) → LLM 抽取（JSON array of {title, questions[]}）
             **严格约束：只能从 context 中实际出现的内容抽取，不得编造。**
Step 4. 对每道新 P2，按 prompt 生成 3-4 道 linked P3（discussion / opinion / comparison / trend）。
Step 5. UPSERT 入库：按 (title, part) 幂等；命中则刷新 season / updated_at / source_url。
Step 6. 回退策略：
        - 无搜索 Key → 直接失败并报 "search_provider_not_configured"
        - 抓取全部失败 → 保留旧题库，不清空，不编造
        - LLM 抽取为空 → 返回 by_part.Pn=0 并列出 source_urls 供人工排查
Output:
  {
    "source": "scraped",
    "current_season": "YYYY-QX",
    "by_part": {"P1": int, "P2": int, "P3": int},
    "derived_p3": int,
    "imported": int, "updated": int,
    "source_urls": [str], "errors": [str]
  }
```

#### 关键幂等与安全
- 不清空旧题库；仅 UPSERT。
- season 字段作为唯一排序锚点：`YYYY-Q{1|2|3}`。
- P3 仅通过衍生生成，禁止网络抓取“P3 真题”作为事实来源。
- 所有抽取调用必须携带 system prompt：`Only include topics that ACTUALLY APPEAR in the context below. Do NOT invent.`

### 相关 API 速查
| 端点 | 作用 |
|------|------|
| `GET /api/topics/meta` | 当前季度、最近更新、是否 stale、Key 配置状态 |
| `POST /api/topics/scrape` | 触发完整抓取+抽取+P3 衍生流水线 |
| `POST /api/topics/backfill-p3?limit=N` | 为已有 P2 批量补全 linked P3 |
| `GET /api/settings/search/providers` | 10 个 provider 元信息（group=api/local） |
| `POST /api/settings/search/test` | 测试搜索 provider 连通性 |
