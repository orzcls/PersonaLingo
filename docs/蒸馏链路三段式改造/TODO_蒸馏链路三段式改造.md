# TODO_蒸馏链路三段式改造 —— 遗留项与操作指引

> 本次改造已全部落地，以下为**用户需手动完成的配置**与**可选后续优化项**。

---

## 1. 必须手动配置（.env）

在 `PersonaLingo/backend/.env` 中按需追加：

```ini
# ── 三段式蒸馏（三段式 Distill Pipeline）────────────────────────
# 是否开启 Stage 1 深度调研中的网络搜索（默认 false，避免外部依赖）
DISTILL_RESEARCH_WEB_SEARCH=false

# 可运行 Skill 包落盘根目录（留空则自动 = <PersonaLingo>/skills/runnable/）
# 示例：
#   SKILL_RUNNABLE_OUT_ROOT=C:/Users/admin/Desktop/PersonaLingo/skills/runnable
SKILL_RUNNABLE_OUT_ROOT=
```

> ⚠️ 若 `SKILL_RUNNABLE_OUT_ROOT` 填绝对路径且目录不存在，`export_runnable_skill` 会自动 `mkdir -p`。

---

## 2. 数据库迁移说明

**无需手动 SQL**。`backend/app/database.py` 中的 `init_db()` 已在启动时幂等执行：

```python
await _add_column_if_missing(db, "corpora", "learner_profile", "TEXT")
await _add_column_if_missing(db, "corpora", "capability_framework", "TEXT")
```

即：
- 全新部署 → 直接生效
- 旧库升级 → 启动时自动加列，不丢数据
- 重复启动 → 幂等无副作用

---

## 3. 启动与验证步骤

```bash
# 1. 后端（PowerShell）
cd PersonaLingo\backend
pip install -r requirements.txt       # 无新增依赖
python run.py                          # 启动时会打印 "Corpora table migrated"

# 2. 验证单测
python -m pytest tests/ -v             # 期望 20 passed（含 P2-3/P2-7 新增 7 条）

# 3. 端到端冒烟（curl / Postman）
#    Step 1：已有 questionnaire_id=xxx
curl -X POST "http://localhost:9849/api/distill/run?questionnaire_id=xxx&include_research=true"
#    Step 2：等待 progress（复用现有 /api/corpus/progress/{corpus_id}）
#    Step 3：产出可运行 Skill 包
curl "http://localhost:9849/api/distill/skill/<corpus_id>/runnable"
#    Step 4：下载 zip（P2-7: FileResponse + 临时文件）
curl -O "http://localhost:9849/api/distill/skill/<corpus_id>/runnable/download"
#    Step 5：在线预览 Skill.md（P2-3：免下载解压）
curl "http://localhost:9849/api/distill/skill/<corpus_id>/runnable/preview?format=markdown"
curl "http://localhost:9849/api/distill/skill/<corpus_id>/runnable/preview?format=html"
```

---

## 4. 后续可选优化（P2，非阻塞）

> ✅ 标记 = 已在 2026-05 落地；其余项保持规划状态。

| # | 项目 | 说明 | 状态 | 预估工作量 |
|---|------|------|------|-----------|
| 1 | Stage 1 网络搜索接入 | 将 `DISTILL_RESEARCH_WEB_SEARCH=true` 时接入已有 `web_search` provider，丰富 topic_signals | ⯑ 待做 | 0.5d |
| 2 | 前端 UI 暴露新端点 | 在 `Questionnaire` 视图加“三段式蒸馏”开关，展示 `learner_profile` / `capability_framework` 预览 | ⯑ 待做 | 1d |
| 3 | Skill 包在线预览 | `GET /api/distill/skill/{id}/runnable/preview?format=markdown\|html`，直返 Skill.md 或极简 HTML渲染 | ✅ **已实现**（P2-3） | ~~0.3d~~ |
| 4 | Stage 2 Prompt 多语言 | 目前 Framework prompt 为中文；可增加 `locale` 参数支持英文输出 | ⯑ 待做 | 0.5d |
| 5 | 扩展 capability_framework 可视化 | 前端加一个 Mermaid 矩阵/雷达图展示 pain_points 与 lift_paths | ⯑ 待做 | 1d |
| 6 | Stage 1 materials 摘要缓存 | 当前每次 research 重跑词频；可为 corpus_id 缓存 language_samples | ⯑ 待做 | 0.5d |
| 7 | zip 下载改 FileResponse | 换下内存流→临时文件+FileResponse，降大语料内存压力 | ✅ **已实现**（P2-7） | ~~0.3d~~ |
| 8 | 多语种 README 第 3 方章节同步 | 若未来加日/韩 README，需要补上三段式段落 | ⯑ 待做 | 视情况 |

---

## 5. 文档导航

| 用途 | 路径 |
|------|------|
| 需求对齐 | `docs/蒸馏链路三段式改造/ALIGNMENT_*.md` |
| 技术共识 | `docs/蒸馏链路三段式改造/CONSENSUS_*.md` |
| 架构设计 | `docs/蒸馏链路三段式改造/DESIGN_*.md` |
| 任务拆分 | `docs/蒸馏链路三段式改造/TASK_*.md` |
| 验收清单 | `docs/蒸馏链路三段式改造/ACCEPTANCE_*.md` |
| 总结报告 | `docs/蒸馏链路三段式改造/FINAL_*.md` |
| Skill 协议 | `skills/personalingo_skill.md` |
| 用户文档 | `README.md` / `README_CN.md` → "核心工作流" |

---

## 6. 已知限制

1. **Stage 1 语料采样上限**：`MAX_MATERIALS=10`, `MAX_CONVERSATIONS=30`。超量学习者将只取最近记录，如需全量分析请修改常量或引入分页。
2. **LLM 结构化输出容错**：`_safe_json` 能处理 ```json``` 代码块包裹，但若 LLM 返回严重偏离 schema，会走 `_fallback`（日志 `warning` 可追踪）。
3. **Windows 路径**：`export_runnable_skill` 使用 `pathlib.Path`，跨平台安全；但 `SKILL_RUNNABLE_OUT_ROOT` 建议使用正斜杠或双反斜杠以避免 `.env` 转义问题。

---

**6A+5S 工作流结束。所有产物已提交，欢迎下一阶段迭代。** 🎯
