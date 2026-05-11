# Distill Protocol — 7 步蒸馏（纯 Agent 内闭环）

> 本 protocol 与后端 `backend/app/services/corpus_generator.py` + `learner_researcher.py` + `capability_framework.py` 的 7 步流程**一一对应**，保证 install-only 模式产出的 `corpus.json` 与 runnable-export 模式结构等价。
> Agent 串行执行 7 步 LLM 调用，每步输入/输出都是 JSON 片段，最终合并成 `corpus/<corpus_id>/corpus.json`，必须通过 `corpus-schema.json` 校验。

## 通用输入（所有 Stage 共享）

- `corpus/<corpus_id>/answers.json` — 问卷原始作答
- `corpus/<corpus_id>/dialogue.md` — 引导对话日志的 Summary 段
- **`skill-assets/band-strategies.json`** — **必须在 Stage 3-7 的每个 system prompt 里注入对应 target_band 的策略块**（词汇分层 / 语法结构 / 时长控制 / 流利度容忍度）。若 `target_band` 为 `8.0+` 或 `暂不考试`，兜底使用 `7.5` 策略。

## 通用输出协议

每个 Stage 完成后，在 `skill_manifest.stages[]` 追加一条记录：

```json
{ "name": "<stage_name>", "status": "completed|fallback|skipped|failed", "source": "llm|rule_fallback|asset_fallback", "note": "..." }
```

---

## Stage 1 · Research（深度调研）

**对应后端**：`learner_researcher.py::run()`
**目标**：聚合 questionnaire + dialogue，产出 `learner_profile`。

**Prompt 核心**：

```
你是学习者画像分析师。输入问卷与对话摘要，输出 JSON 对象 learner_profile：
{
  "background": "一段话概述学习者身份（学校/专业/职业/目标）",
  "goal_vector": { "target_band": "6.0|6.5|7.0|7.5", "exam_window": "30天内|1-3月|3-6月|半年+", "current_band": string | null },
  "strengths": ["具体能力点..."],
  "weakness_signals": ["可观测薄弱项（必须带证据句子）..."],
  "language_samples": ["原样摘抄的学习者英文或中文样本句..."],
  "topic_signals": {
    "total": int,
    "matches": [{ "id": "string", "part": "P1|P2|P3", "title": "string", "category": "string" }]
  },
  "source_stats": { "materials": 0, "chats": int, "topics": int },
  "web_enabled": false,
  "generated_at": "<ISO-8601>"
}
要求：具体、可引用、不要总结成形容词；弱项必须带证据；install-only 模式下 `materials` 恒为 0。
```

**降级（Install-only 不可达外部资源时）**：
- 无 dialogue → `language_samples=[]`、`weakness_signals` 仅从问卷 `weaknesses` 段映射
- status=`fallback`，source=`rule_fallback`，note=`"no dialogue captured"`

---

## Stage 2 · Framework（能力框架）

**对应后端**：`capability_framework.py::run()`
**目标**：能力 × 场景 × 目标三维矩阵 + 痛点 + 提升路径。

**Prompt 核心**：

```
基于 learner_profile，输出 capability_framework：
{
  "source": "llm",
  "dimensions": {
    "ability":  [
      { "name": "lexical_range", "current": "6.0", "target": "6.5", "notes": "vocabulary upgrade for target band" },
      { "name": "fluency",       "current": "6.0", "target": "6.5", "notes": "increase sentence length and connectors" }
    ],
    "scenario": [
      { "part": "P1", "topics": ["work","hometown"], "priority": "high" },
      { "part": "P2", "topics": ["a person you admire"], "priority": "medium" }
    ],
    "goal": [
      { "key": "target_score",    "value": "6.5" },
      { "key": "priority_parts",  "value": "P1,P2" }
    ]
  },
  "pain_points": [
    { "id": "pp1", "desc": "Sentences are too short; needs longer clauses with subordinators.", "signals": ["short_sentences"] }
  ],
  "lift_paths": [
    { "from": "6.0", "to": "6.5", "steps": ["Build 3-4 personal anchor stories", "Upgrade 25-30 high-impact vocab", "Drill 8-10 sentence patterns"] }
  ]
}
每个 pain_point 必须带 `signals`（来自 learner_profile.weakness_signals）；dimensions 三组至少各 2 项；lift_paths.steps 描述具体动作。
```

**降级**：LLM 失败 → 使用最小可用骨架（与后端 `capability_framework._rule_fallback()` 对齐）：
```json
{ "source": "rule_fallback",
  "dimensions": {
    "ability":  [{"name":"lexical_range","current":"6.0","target":"6.5","notes":"vocabulary upgrade for target band"}],
    "scenario": [{"part":"P1","topics":[],"priority":"high"}],
    "goal":     [{"key":"target_score","value":"6.5"}]
  },
  "pain_points": [{"id":"pp0","desc":"No weakness signals detected; build baseline anchors first.","signals":[]}],
  "lift_paths":  [{"from":"6.0","to":"6.5","steps":["Practice more"]}] }
```
status=`fallback`，source=`rule_fallback`。

---

## Stage 3 · Persona（MBTI + 沟通风格）

**对应后端**：`corpus_generator.generate_persona()`
**目标**：MBTI 四维度 + 沟通风格。

**Prompt 核心**（必须注入 band_strategy）：

```
[SYSTEM]
Target band: {target_band}
Band strategy (from band-strategies.json):
  vocabulary: {band.vocabulary}
  grammar:    {band.grammar}
  fluency:    {band.fluency}
Respect these constraints when inferring communication style.

[USER]
基于 answers.persona.mbti + communication_style + learner_profile.language_samples，输出 persona：
{
  "mbti": "XXXX" | "unknown",
  "dimensions": {
    "EI": { "score": -3..+3, "evidence": "..." },
    "SN": { "score": -3..+3, "evidence": "..." },
    "TF": { "score": -3..+3, "evidence": "..." },
    "JP": { "score": -3..+3, "evidence": "..." }
  },
  "communication_style": {
    "opener_pattern":    "如何起头一段回答（与 band_strategy.fluency.filler_strategy 一致）",
    "structure_pattern": "S-C-R | PREP | STAR | other",
    "closing_pattern":   "如何收束（参考 band_strategy.timing.safe_stop_strategy）",
    "avoid":             ["不符合此学习者风格/分数段的表达..."]
  }
}
MBTI 为 unknown 时：基于 language_samples 做弱推断并在每个维度的 `evidence` 中声明 "uncertain"（注意：此处 dimensions 是 persona.dimensions，结构为 {EI/SN/TF/JP}，与 capability_framework.dimensions 不同）。
```

**降级**：LLM 失败 → `mbti="unknown"`，`communication_style` 取 `band_strategy` 默认值（PREP 结构）。status=`fallback`，source=`rule_fallback`。

---

## Stage 4 · Anchors（锚点故事）

**对应后端**：`corpus_generator.generate_anchors()`
**目标**：3-4 个可复用的个人核心故事。

**Prompt 核心**（必须注入 band_strategy）：

```
[SYSTEM]
Respect band_strategy.vocabulary.level and grammar.complexity when writing story_beats.
Avoid list: {band.vocabulary.avoid ∪ band.grammar.avoid}

[USER]
从 answers.experiences.{people, objects, places, events} + dialogue.md 提取 3-4 个 anchor：
{
  "anchors": [
    {
      "id": "A-01",
      "title": "一句话英文标题",
      "category": "person | object | place | event | abstract",
      "one_liner": "英文一句话摘要（≤25 words）",
      "story_beats": ["beat 1", "beat 2", "beat 3"],
      "keywords": ["3-5 个核心英文关键词"],
      "emotion_tag": "pride | regret | growth | curiosity | frustration | ...",
      "reusable_for_topics": ["2-4 个 IELTS P2/P3 话题示例"],
      "connectable_topics": ["同上，与后端 AnchorStory.connectable_topics 对齐的别名"]
    }
  ]
}
硬约束：锚点必须是真实发生过的具体事件，禁止虚构；故事细节必须能从 answers/dialogue 中引用到。
```

**降级**：LLM 失败 / 真实素材不足 → 直接把 `answers.experiences.events[]` 前 3 条映射为 anchor（`title=事件名`，`category="event"`，`story_beats=[用户原文拆分]`，`keywords=[]`）。status=`fallback`，source=`user_input`。

---

## Stage 5 · Bridges（题库桥接）

**对应后端**：`corpus_generator.generate_bridges()`
**目标**：将锚点桥接到 15-28 个 IELTS 话题。

**输入题库**：优先使用 `skill-assets/fallback-topics.json`（20 个 P1/P2 经典话题）；若用户在 dialogue 中提到特殊话题可额外补充。

**Prompt 核心**（必须注入 band_strategy）：

```
[SYSTEM]
Band-appropriate style:
  timing.p1_target_seconds = {band.timing.p1_target_seconds}
  safe_stop_strategy       = {band.timing.safe_stop_strategy}
  filler_strategy          = {band.fluency.filler_strategy}

[USER]
从 fallback-topics.json 取 10 条 P1 + 5 条 P2，结合 anchors，产出 15-28 个 bridges：
{
  "bridges": [
    {
      "id": "B-01",
      "anchor_id": "A-01",
      "topic_id": "T-03",
      "topic": "Hobbies and free time",
      "category": "abstract",
      "question_type": "preference",
      "bridge_sentence": "Well, this actually ties back to the summer I spent coding for ICPC...",
      "hook_sentence": "Well, this actually ties back to ...",
      "sample_answer": "30-60 words，体现 band_strategy.grammar.structures 中的 1-2 个结构",
      "safe_stop_point": "与 band.timing.safe_stop_strategy 一致的收束句",
      "techniques_used": ["anchor_callback", "personal_example"],
      "transition_phrase": "which reminds me of ..."
    }
  ]
}
硬约束：
- 每个 anchor 至少绑定 3 个 bridge；
- sample_answer 长度由 target_band 决定（见 band.timing.p1_target_seconds * 2.5 words）；
- question_type 需从 {preference, opinion, description, experience, factual} 中选取。
```

**降级**：LLM 失败 → 为每个 anchor 生成 3 条 bridge（仅 `anchor_id + topic + bridge_sentence`，其他字段空字符串）。status=`fallback`，source=`asset_fallback`，note=`"used fallback-topics.json only, no LLM"`。

---

## Stage 6 · Vocabulary（词汇升级）

**对应后端**：`corpus_generator.generate_vocabulary()`
**目标**：25-30 个带段位标签的词汇/搭配。

**输入词表**：优先从 `language_samples` + `anchors.story_beats` 提取；若样本不足，从 `skill-assets/fallback-vocabulary.json` 按 `target_band ± 0.5` 档位补齐。

**Prompt 核心**（必须注入 band_strategy）：

```
[SYSTEM]
upgrade_ratio = {band.vocabulary.upgrade_ratio}  # 多少比例的词需要升级
avoid         = {band.vocabulary.avoid}

[USER]
基于 language_samples + anchors.story_beats，输出 25-30 条 vocabulary：
[
  {
    "item": "grapple with",
    "basic_word": "deal with",
    "upgrade": "grapple with",
    "type": "phrase",
    "band_tier": "7.0",
    "native_equivalent": "struggle with",
    "context": "challenge / difficulty",
    "example_from_anchor": "A-01: I had to grapple with a DP problem I'd never seen.",
    "category": "challenge",
    "qmd_tags": ["effort", "challenge"]
  }
]
硬约束：
- 每个词必须给出基于具体 anchor 的真实例句，禁止造句；
- band_tier ∈ {6.0, 6.5, 7.0, 7.5}，按 upgrade_ratio 分布；
- 禁止使用 band.vocabulary.avoid 列表中的类型。
```

**降级**：LLM 失败 / `language_samples.length < 3` → 从 `fallback-vocabulary.json` 对应 band 档位取 10 条 + 上下一档各 5-10 条，`example_from_anchor` 留空字符串。status=`fallback`，source=`asset_fallback`。

---

## Stage 7 · Patterns（句型模板）

**对应后端**：`corpus_generator.generate_patterns()`
**目标**：8-10 个 MBTI 匹配的句型骨架。

**Prompt 核心**（必须注入 persona.communication_style）：

```
[USER]
基于 persona.mbti + persona.communication_style，输出 8-10 条 patterns：
[
  {
    "id": "P-01",
    "name": "Anchor-based opener",
    "purpose": "opener | structure | contrast | emphasis | closing",
    "skeleton": "What really got me thinking was _____ because _____.",
    "formula": "Hook + Reason",
    "when_to_use": "当被问到 personal experience / opinion 时",
    "fits_mbti": ["INTJ", "INTP"],
    "example_from_anchor": "A-02: What really got me thinking was the silence in the cockpit because..."
  }
]
硬约束：
- 每个 purpose 至少 1 条；
- fits_mbti 必须与 persona.mbti 有交集或设为 ["ALL"]；
- 每条必须引用一个已生成的 anchor id。
```

**降级**：LLM 失败 / persona.mbti=unknown → 直接从 `skill-assets/fallback-patterns.json` 加载 8 条通用模板（`fits_mbti=["ALL"]`）。status=`fallback`，source=`asset_fallback`。

---

## 合并输出

最终 `corpus/<corpus_id>/corpus.json` 的顶层字段：

```json
{
  "skill_manifest": {
    "name": "personalingo",
    "version": "3.1.0",
    "mode": "install-only",
    "pipeline": "three_stage_distill",
    "generated_at": "<ISO-8601>",
    "stages": [
      { "name": "research",   "status": "completed", "source": "llm" },
      { "name": "framework",  "status": "completed", "source": "llm" },
      { "name": "persona",    "status": "completed", "source": "llm" },
      { "name": "anchors",    "status": "completed", "source": "llm" },
      { "name": "bridges",    "status": "completed", "source": "llm" },
      { "name": "vocabulary", "status": "completed", "source": "llm" },
      { "name": "patterns",   "status": "completed", "source": "llm" }
    ]
  },
  "learner_profile":      { ... },
  "capability_framework": { ... },
  "persona":              { ... },
  "anchors":              [ ... ],
  "bridges":              [ ... ],
  "vocabulary":           [ ... ],
  "patterns":             [ ... ],
  "band_strategy":        { "band": "7.0", "vocabulary": {...}, "grammar": {...}, "timing": {...}, "fluency": {...} }
}
```

Agent **必须**在写入前用 `corpus-schema.json` 做 JSON Schema 校验，不符字段直接丢弃并记录到 `stages[i].note`。

---

## 降级策略速查表（install-only 可执行版）

| 阶段失败 | 触发条件 | 降级动作 | 落地字段 | source |
|---|---|---|---|---|
| Stage 1 Research | 无 dialogue 数据 | 从 answers 映射最小 profile；`language_samples=[]` | `source_stats.chats=0` | `rule_fallback` |
| Stage 2 Framework | LLM 失败 / 无效 JSON | 使用 `_rule_fallback()` 等价最小骨架（≥1 PP + ≥1 lift_path） | `source:"rule_fallback"` | `rule_fallback` |
| Stage 3 Persona | LLM 失败 / mbti=unknown | 取 band_strategy 默认 PREP 结构；dimensions 留空 | `mbti:"unknown"` | `rule_fallback` |
| Stage 4 Anchors | LLM 失败 / experiences 为空 | 从 answers.experiences.events 前 3 条直映射为 anchor | `category:"event"` | `user_input` |
| Stage 5 Bridges | LLM 失败 | 为每个 anchor 从 fallback-topics.json 取 3 条话题 | `techniques_used:[]` | `asset_fallback` |
| Stage 6 Vocabulary | LLM 失败 / samples<3 | 从 fallback-vocabulary.json 取 target_band ± 0.5 档共 25 条 | `example_from_anchor:""` | `asset_fallback` |
| Stage 7 Patterns | LLM 失败 / mbti=unknown | 加载 fallback-patterns.json 全 8 条 | `fits_mbti:["ALL"]` | `asset_fallback` |

**规则**：
- 每次降级都必须在 `skill_manifest.stages[i]` 写 `status="fallback"` + `source` + `note`。
- **不允许**直接 `skip` 必需字段（anchors/bridges/vocabulary/patterns）：Schema 的 `required` 要求它们非空，因此降级必须保证产物有内容。
- `practices` 为可选产物，失败时可 `status="skipped"`。

## 与 runnable-export 模式的结构等价性

Install-only 产物与 runnable-export 产物遵循**同一 schema**（`corpus-schema.json`），差异只在：
- `skill_manifest.mode` = `install-only` vs `runnable-export`
- `user_style` 仅 runnable-export 填充（需后端 conversation-engine 统计）
- `learner_profile.web_enabled` / `source_stats.materials` 仅 runnable-export 非零

下游 Agent 可用相同逻辑读取两种模式的 corpus.json，这是"一键安装 = 真实蒸馏"承诺的结构保证。
