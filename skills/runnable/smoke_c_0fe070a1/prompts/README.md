# Prompts Index

本 Skill 的运行时 prompt 模板集中维护在仓库代码仓(不随包导出以保持可维护性):

| Stage | 文件 | 符号 |
|---|---|---|
| Stage 2 框架提炼 | `backend/app/services/capability_framework.py` | `FRAMEWORK_SYSTEM`, `FRAMEWORK_USER` |
| Stage 3 语料生成 | `backend/app/services/corpus_generator_prompts.py` | `PERSONA_*`, `ANCHORS_*`, `BRIDGES_*`, `VOCABULARY_*`, `PATTERNS_*`, `PRACTICES_*` |
| QMD 检索 | `backend/app/services/qmd_engine.py` | `QUERY_EXPANSION_PROMPT` |

若需内联 prompt,可覆写本目录下的 `stage3_persona.txt` 等文件;Skill 加载会优先采用本地文件。
