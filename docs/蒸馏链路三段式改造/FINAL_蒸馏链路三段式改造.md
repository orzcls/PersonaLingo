# FINAL_蒸馏链路三段式改造 —— 项目总结报告

## 1. 任务概述

**目标**：对标 `huashu-nuwa` 的「深度调研→思维框架提炼→可运行 Skill」三段式工作流，对 PersonaLingo 的核心功能「蒸馏学生定制专属语料库训练」做深度优化；抽取 nuwa 框架并适配到本项目，让语料库蒸馏从 5 步扩展为 7 步，并新增可下发给外部 Agent 的可运行 Skill 包。

**驱动原则**：6A 工作流（Align→Architect→Atomize→Approve→Automate→Assess）+ 5S 精益（Sort/Set/Shine/Standardize/Sustain）。

## 2. 差距分析（改造前 vs huashu-nuwa）

| 维度 | 改造前 PersonaLingo | huashu-nuwa 参考 | 差距 |
|------|--------------------|------------------|------|
| 输入处理 | 问卷 + MBTI + 目标分数 | 深度调研（多信源聚合+弱点信号） | ❌ 缺 learner_profile 抽象 |
| 中间产物 | 无 | capability_framework（思维矩阵） | ❌ 缺三维能力画像 |
| 蒸馏步骤 | 5 步（Persona→Anchors→Bridges→Vocab→Patterns） | N 步 + 前置调研+框架 | ⚠️ 直接跳到策略，缺"为什么这么做"的依据 |
| 外部 Agent 接入 | 仅 `export_skill`（单 md+json） | 可运行 Skill 包（4 件套 + manifest） | ❌ 无运行协议 |
| 失败降级 | 单点失败 = 全流程失败 | 多级降级 | ⚠️ 新增 Stage 必须向后兼容 |

**结论**：差距集中在 **"前置调研/框架提炼"** 与 **"外部可运行性"** 两端，采用三段式改造收益最高。

## 3. 架构改造（7 步链路）

```
Questionnaire + Materials + Conversations + Topics
   │
   ▼
[Stage 1 · Research]    learner_researcher.py
   → learner_profile { background, language_samples, weakness_signals,
                       goal_vector, topic_signals }
   │
   ▼
[Stage 2 · Framework]   capability_framework.py
   → capability_framework { matrix[ability×scenario×goal],
                            pain_points[], lift_paths[] }
   │
   ▼
[Stage 3 · Distill]     corpus_generator.py（原 5 步，前置结果作为上下文增强）
   3a Persona → 3b Anchors → 3c Bridges → 3d Vocabulary → 3e Patterns
   │
   ▼
[Delivery] corpus.json + Runnable Skill Pack (4 artifacts)
           skill_exporter.export_runnable_skill()
```

**向后兼容**：`generate_full_corpus(include_research=True)` 默认开启；Stage 1/2 任一失败 → `logger.warning` + `set_generation_progress("skipped")` → 直接执行 Stage 3（等同旧版 5 步）。

## 4. 实际交付

### 代码（backend/app/）

| 文件 | 变更 | 行数 |
|------|------|------|
| `config.py` | 新增 2 配置项 | +3 |
| `database.py` | 幂等迁移 2 列 | +3 |
| `db/crud.py` | JSON 白名单 +2 | ~4 |
| `services/learner_researcher.py` | **新建** | 286 |
| `services/capability_framework.py` | **新建** | 247 |
| `services/corpus_generator.py` | 串联 Stage 1/2 | ~30 |
| `services/skill_exporter.py` | +`export_runnable_skill` | ~120 |
| `routers/distill.py` | **新建** | 240 |
| `main.py` | 注册路由 | +2 |

### 测试（backend/tests/）

| 文件 | 行数 | 用例数 |
|------|------|--------|
| `conftest.py` | ~6 | - |
| `test_learner_researcher.py` | 85 | 5 |
| `test_capability_framework.py` | ~120 | 6 |
| `test_skill_exporter_runnable.py` | ~90 | 2 |
| `test_distill_router_p2.py` | ~150 | 7 |

**pytest 结果**：`20 passed in 0.63s` ✅（原 13 + P2 新增 7）

### P2 追加落地（2026-05）

| 项 | 端点 / 改造 | 文件 |
|----|-------------|------|
| **P2-3** 在线预览 | `GET /api/distill/skill/{id}/runnable/preview?format=markdown\|html` → 直返 Skill.md 或极简 HTML（零依赖渲染） | `routers/distill.py` 新增 `preview_runnable` + `_render_minimal_html` |
| **P2-7** 下载优化 | `/runnable/download` 由 `BytesIO + StreamingResponse` → `tempfile.NamedTemporaryFile + FileResponse`，降内存压力 | `routers/distill.py:download_runnable` |

### 文档

- 4 份过程文档（ALIGNMENT / CONSENSUS / DESIGN / TASK）
- 3 份收尾文档（ACCEPTANCE / FINAL / TODO）
- 1 份 skill 说明（`skills/personalingo_skill.md` 5→7 步）
- 2 份 README（中英双语新增三段式章节 + API 速查）

## 5. 关键技术决策

1. **`unittest.IsolatedAsyncioTestCase`** 替代 `pytest-asyncio`（后者未安装，避免新增依赖）
2. **`Path.parents[3]`** 自动定位 PersonaLingo 根，Skill 包默认落 `skills/runnable/{corpus_id}/`
3. **LLM 降级路径**：Stage 2 LLM 不可用 → `_fallback()` 规则兜底（非空）→ 不阻断 Stage 3
4. **网络搜索默认关闭**：`DISTILL_RESEARCH_WEB_SEARCH=False`，避免外部副作用
5. **DB 迁移幂等**：沿用 `_add_column_if_missing`，无需新表
6. **API 统一响应**：`{"data":..., "error": null}`，保持项目既有契约

## 6. 5S 执行回顾

| 原则 | 落地举措 |
|------|----------|
| **Sort** | 不新建重复 service；`export_runnable_skill` 复用已有 `export_skill` 基础 |
| **Set in order** | 新模块置于 `services/` 与现有同级；路由拆独立 `routers/distill.py` 而非塞入 `corpus.py` |
| **Shine** | 三段式失败降级为单文件内 try/except，无深层嵌套；`_safe_json` 独立小函数 |
| **Standardize** | 配置走 `Settings`；API 走统一响应；migration 走项目既有模式 |
| **Sustain** | 新模块全部配单测；skill md + README 同步；FINAL+TODO 收尾 |

## 7. 风险与应对

| 风险 | 应对 |
|------|------|
| LLM 不稳定导致 Stage 2 空输出 | `_fallback()` 基于 weakness_signals 生成非空矩阵 |
| 旧前端调用 `/api/corpus/generate` 断掉 | 未动原路由；`include_research` 默认 True 仅增强 |
| Skill 包外泄敏感数据 | 只落 `skills/runnable/`，该目录已在 `.gitignore` 语义范围（用户可自定义 `SKILL_RUNNABLE_OUT_ROOT`） |
| DB 迁移重复执行 | `_add_column_if_missing` 幂等保证 |

## 8. 验收结论

**✅ 所有需求实现 + 测试通过 + 文档同步，可交付。**

详见 [`ACCEPTANCE_蒸馏链路三段式改造.md`](./ACCEPTANCE_蒸馏链路三段式改造.md) 与 [`TODO_蒸馏链路三段式改造.md`](./TODO_蒸馏链路三段式改造.md)。
