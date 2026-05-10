# ACCEPTANCE_蒸馏链路三段式改造

> 完工验收清单。勾选 = 已实现 + 已验证（AST/单测/文档同步均通过）。

## 交付物清单

### 代码交付（backend/app/）

- [x] **T1**：`config.py` 新增 `DISTILL_RESEARCH_WEB_SEARCH` / `SKILL_RUNNABLE_OUT_ROOT`；`database.py` 幂等迁移 `corpora` 表新增 `learner_profile` / `capability_framework` 列；`db/crud.py` 扩展 JSON 字段白名单。
- [x] **T2**：`services/learner_researcher.py`（286 行）—— Stage 1 深度调研，聚合问卷/资料/对话/主题，产出 `LearnerProfile`；提供 `get_learner_researcher()` 工厂；规则工具 `_avg_sentence_length` / `_count_connectors` / `_derive_weakness_signals`。
- [x] **T3**：`services/capability_framework.py`（247 行）—— Stage 2 框架提炼，三维矩阵（ability×scenario×goal）+ pain_points + lift_paths；LLM 失败自动规则兜底。
- [x] **T4**：`services/corpus_generator.py` —— `generate_full_corpus` 新增 `include_research` 参数（默认 True），在原 5 步前串联 Stage 1/2；Stage 1/2 失败只 `warning` + `skipped`，不阻断 Stage 3。
- [x] **T5**：`services/skill_exporter.py` —— 新增 `export_runnable_skill(corpus_id, out_root=None)`，产出 4 件套（`Skill.md` + `corpus.json` + `runtime_protocol.md` + `prompts/README.md`），内置 `skill_manifest`。
- [x] **T6**：`routers/distill.py`（240 行）—— 4 个端点（`/diagnose` / `/run` / `/skill/{id}/runnable` / `/skill/{id}/runnable/download`）；`main.py` 注册 `/api/distill` 前缀。

### 测试交付（backend/tests/）

- [x] `conftest.py` —— 将 `backend/` 加入 `sys.path`，保证 `app.*` 导入。
- [x] `test_learner_researcher.py` —— 3 个规则单测 + 2 个 async 单测（空问卷降级 / 全材料路径）。
- [x] `test_capability_framework.py` —— 4 个同步单测 + 2 个 async 单测（LLM 失败降级 / 非 dict 输入）。
- [x] `test_skill_exporter_runnable.py` —— 2 个 async 单测（4 件套齐全 / 缺失 corpus 抛错）。
- [x] **最终结果**：`pytest tests/ -v` 全绿（**13 passed**）。

### 文档交付

- [x] `docs/蒸馏链路三段式改造/ALIGNMENT_*.md` —— 需求对齐 + 边界澄清
- [x] `docs/蒸馏链路三段式改造/CONSENSUS_*.md` —— 技术方案共识
- [x] `docs/蒸馏链路三段式改造/DESIGN_*.md` —— 架构设计（含 Mermaid 链路图 + 契约）
- [x] `docs/蒸馏链路三段式改造/TASK_*.md` —— 原子任务拆分（含依赖图）
- [x] `docs/蒸馏链路三段式改造/ACCEPTANCE_*.md` —— 本文件
- [x] `docs/蒸馏链路三段式改造/FINAL_*.md` —— 总结报告
- [x] `docs/蒸馏链路三段式改造/TODO_*.md` —— 遗留项与 `.env` 配置指引
- [x] `skills/personalingo_skill.md` —— 5 步 → 7 步，新增可运行 Skill 协议章节
- [x] `README.md` / `README_CN.md` —— 核心工作流章节升级为三段式描述 + API 速查

## 质量门禁

| 维度 | 标准 | 结果 |
|------|------|------|
| 语法 | 所有新/改文件 AST 解析通过 | ✅ AST_OK |
| 单测 | pytest 全通过 | ✅ 13/13 passed (0.18s) |
| 向后兼容 | 旧 `POST /api/corpus/generate` 不变、Stage 1/2 失败不阻断 | ✅ `include_research=True` 默认 + 双层 try 降级 |
| 密钥安全 | 无硬编码 key；新增配置项纳入 `Settings` | ✅ 经 `pydantic-settings` 管理 |
| 幂等迁移 | DB 新列使用 `_add_column_if_missing` | ✅ 项目既有模式 |
| 文档同步 | skill md + 双语 README + 4 份过程文档 | ✅ 完成 |

## 验收结论

**✅ 全部通过，可进入 Sustain 阶段。**
