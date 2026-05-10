# CONSENSUS — 蒸馏链路三段式改造

## 1. 明确需求描述
将 PersonaLingo 核心功能「学生定制专属语料库蒸馏」从**5步线性生成**升级为对齐 huashu-nuwa 的**三段式链路**:

```
Entry Router(明确/模糊双入口)
   ↓
Stage 1  Research  深度调研 → LearnerProfile
   ↓
Stage 2  Framework 框架提炼 → CapabilityFramework
   ↓
Stage 3  Distill   Persona → Anchors → Bridges → Vocabulary → Patterns → Runnable Skill Pack
```

## 2. 技术方案

| 模块 | 实现 | 依赖 |
|---|---|---|
| `LearnerResearcher` | 纯 Python + LLM 聚合本地信息源(可选网络) | `llm_adapter`, `crud.get_*` |
| `CapabilityFramework` | LLM 抽象 + 规则兜底 | `llm_adapter` |
| `CorpusGenerator.generate_full_corpus` | 前置插入 Stage 1/2;向下兼容参数 | 现有 5 步不动 |
| `SkillExporter.export_runnable_skill` | 写出目录:`Skill.md + corpus.json + runtime_protocol.md + prompts/` | `skill_exporter` 扩展 |
| `routers/distill.py` | 3 端点:diagnose / run / skill-runnable | `corpus_generator`, `skill_exporter` |
| DB 字段扩展 | 在 `corpora` 表新增 `learner_profile`, `capability_framework` 两列 TEXT(JSON) | `schemas.py`, `crud.py` |

## 3. 技术约束(Sort + Standardize)
- 向后兼容:旧接口 `POST /api/corpus/generate` 行为保持一致;`generate_full_corpus()` 新增可选参数 `include_research: bool = True`,旧调用无需改动
- DB 迁移:使用 `CREATE TABLE IF NOT EXISTS` + 启动时对旧表做 `ALTER TABLE ADD COLUMN IF NOT EXISTS`(SQLite 3.35+) 或 try/except 忽略已存在的列
- API Key:Research 层若启用网络搜索,Key 从 `.env` 读取,禁止硬编码
- 错误处理:Stage 1/2 失败降级为"空档案"+ `logger.warning`,不阻断 Stage 3
- 命名:新服务类名 `LearnerResearcher` / `CapabilityFramework`,文件名 snake_case
- 返回体:新端点遵循 `{ "data": ..., "error": null }` 约定(与现有 settings/distill 风格一致)

## 4. 集成方案
- `main.py` 中 import 并 `include_router(distill.router, prefix="/api/distill", tags=["Distill"])`
- `corpus_generator.py` 的入口函数 `generate_full_corpus()` 在 Step 1 之前串联 Stage 1+2,结果写入对应字段后继续原流程
- `skill_exporter.py` 新增方法,不删除已有 `export_markdown/export_json`

## 5. 任务边界(再次确认)
| 项 | 决策 |
|---|---|
| Research 网络搜索 | 默认关闭,通过 `DISTILL_RESEARCH_WEB_SEARCH=true` 启用 |
| Skill 包路径 | `PersonaLingo/skills/runnable/{corpus_id}/` |
| 双入口 UI | **本期仅做后端端点**,前端展示留 TODO |
| 单测 | pytest,仅覆盖新增模块关键路径(各 1-2 个) |

## 6. 验收标准
沿用 ALIGNMENT §6 的 A1-A6,全部通过即视为本期完成。

## 7. 不确定性与降级
- LLM 不可用 → Stage 1/2 走规则兜底,Stage 3 仍可跑(复用旧 5 步)
- 无 materials / conversation 历史 → Stage 1 仅消费 questionnaire,产物字段置空列表
