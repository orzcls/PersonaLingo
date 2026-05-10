# Distill Protocol — 7 步蒸馏（纯 Agent 内闭环）

> Agent 串行执行 7 步 LLM 调用，每步的输入/输出都是 JSON 片段，最终合并成 `corpus/<corpus_id>/corpus.json`（对齐 Mode A schema）。
> 每步失败时记录错误但**继续降级**到后续步骤（与项目 Mode A 的 fallback 对齐）。

## 通用输入

所有步骤共享以下上下文（从前序产物加载）：

- `answers.json` — 问卷原始作答
- `dialogue.md` — 引导对话日志（取 Summary 段）

## Stage 1 · Research（深度调研）

**目标**：把问卷 + 对话融合为 `learner_profile`。

**Prompt 核心**：

```
你是学习者画像分析师。输入问卷与对话摘要，输出 JSON 对象 learner_profile：
{
  "background": "一段话概述学习者身份",
  "goal_vector": { "target_band": string, "exam_window": string, "current_band": string | null },
  "strengths": ["具体能力点..."],
  "weakness_signals": ["可观测薄弱项..."],
  "language_samples": ["原样摘抄的学习者句子..."]
}
要求：具体、可引用、不要总结成形容词；弱项必须带证据。
```

## Stage 2 · Framework（能力框架）

**目标**：能力 × 场景 × 目标三维矩阵。

**Prompt 核心**：

```
基于 learner_profile，输出 capability_framework：
{
  "pain_points": [ { "id": "PP-01", "name": "...", "evidence": "引用 language_samples 某一句" } ],
  "lift_paths":  [ { "from": "PP-01", "to": "目标能力描述", "band_gap": "6.5→7.0" } ]
}
每个 lift_path 必须绑定一个或多个 pain_point id。
```

## Stage 3 · Persona（用户画像 + MBTI）

**目标**：MBTI 四个维度的沟通风格推断。

**Prompt 核心**：

```
基于 answers.mbti + communication_style + language_samples，输出 persona：
{
  "mbti": "XXXX",
  "dimensions": {
    "EI": { "score": -3..+3, "evidence": "..." },
    "SN": { ... },
    "TF": { ... },
    "JP": { ... }
  },
  "communication_style": {
    "opener_pattern": "如何起头一段回答",
    "structure_pattern": "S-C-R / PREP / 其它",
    "closing_pattern": "如何收束",
    "avoid": ["不符合此学习者风格的表达..."]
  }
}
MBTI 为 unknown 时：基于 language_samples 做弱推断并在 dimensions.*.evidence 中声明 "uncertain"。
```

## Stage 4 · Anchors（锚点故事）

**目标**：3-4 个可复用的个人核心故事。

**Prompt 核心**：

```
从 answers.experiences.{people, objects, places, events} + dialogue.md 提取 3-4 个 anchor：
{
  "anchors": [
    {
      "id": "A-01",
      "title": "一句话标题（英文）",
      "category": "person | object | place | event",
      "one_liner": "英文一句话摘要（<=25 words）",
      "story_beats": ["beat 1", "beat 2", "beat 3"],
      "emotion_tag": "pride | regret | growth | curiosity | ...",
      "reusable_for_topics": ["IELTS P2/P3 话题示例 2-4 个"]
    }
  ]
}
锚点必须是真实发生过的具体事件，禁止虚构。
```

## Stage 5 · Bridges（题库桥接）

**目标**：把锚点桥接到 21 个常见 IELTS 话题。

**Prompt 核心**：

```
为每个 anchor 生成 5-7 个 bridge：
{
  "bridges": [
    {
      "id": "B-01",
      "anchor_id": "A-01",
      "topic": "Describe a place you visited",
      "hook_sentence": "Well, this actually ties back to the summer I spent in ...",
      "transition_phrase": "which reminds me of ..."
    }
  ]
}
全部 anchor 合计 bridge 数在 15-28 之间。
```

## Stage 6 · Vocabulary（词汇升级）

**目标**：25-30 个带段位标签的词汇/搭配。

**Prompt 核心**：

```
基于 target_band + language_samples + anchor story_beats，输出 vocabulary：
[
  {
    "item": "grapple with",
    "type": "phrase",
    "band_tier": "7.0",
    "native_equivalent": "deal with",
    "example_from_anchor": "A-01: I had to grapple with a DP problem I'd never seen.",
    "qmd_tags": ["effort", "challenge"]
  }
]
每个词必须给出基于 anchor 的真实例句，禁止造句。
```

## Stage 7 · Patterns（句型模板）

**目标**：8-10 个 MBTI 匹配的句型骨架。

**Prompt 核心**：

```
基于 persona.communication_style，输出 patterns：
[
  {
    "id": "P-01",
    "purpose": "opener / structure / contrast / emphasis / closing",
    "skeleton": "What really got me thinking was _____ because _____.",
    "fits_mbti": ["INTJ", "INTP"],
    "example_from_anchor": "A-02: What really got me thinking was the silence in the cockpit because..."
  }
]
```

## 合并输出

最终写入 `corpus/<corpus_id>/corpus.json`：

```json
{
  "skill_manifest": {
    "name": "personalingo",
    "version": "3.1",
    "mode": "install-only",
    "pipeline": "three_stage_distill",
    "stages": [
      { "name": "research", "status": "completed" },
      { "name": "framework", "status": "completed" },
      { "name": "persona", "status": "completed" },
      { "name": "anchors", "status": "completed" },
      { "name": "bridges", "status": "completed" },
      { "name": "vocabulary", "status": "completed" },
      { "name": "patterns", "status": "completed" }
    ]
  },
  "learner_profile": { ... },
  "capability_framework": { ... },
  "persona": { ... },
  "anchors": [ ... ],
  "bridges": [ ... ],
  "vocabulary": [ ... ],
  "patterns": [ ... ]
}
```

## 降级策略

| 阶段失败 | 动作 |
|---|---|
| Stage 1 | 用 answers.self_description 填充 learner_profile.background，其它字段留空数组 |
| Stage 2 | 跳过，后续步骤直接基于 learner_profile |
| Stage 3 | mbti = "unknown"，communication_style 用默认 PREP 结构 |
| Stage 4 | 从 events 列表直接映射为 anchor（title = 事件名） |
| Stage 5 | bridges = []，SKILL.md 末尾提示用户手动补 |
| Stage 6 | vocabulary = []，提示用户上传素材后再跑一次 |
| Stage 7 | 使用内置 5 条默认 pattern（见 `fallback-patterns.json` 若存在） |

每次降级都要在 `corpus.json.skill_manifest.stages[i].status` 写 `fallback` 并附 `note` 字段说明原因。
