"""Skill 导出器 - 仅 MD + JSON 两种格式"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.db.crud import get_corpus, get_questionnaire

logger = logging.getLogger(__name__)


class SkillExporter:
    """Skill 导出器 - 仅 Markdown 和 JSON 两种格式"""

    async def export_markdown(self, corpus_id: str) -> str:
        """
        导出 Markdown 格式 Skill 文件
        从数据库读取语料库数据，生成完整的 Markdown 内容
        """
        corpus = await get_corpus(corpus_id)
        if not corpus:
            raise ValueError(f"语料库不存在: {corpus_id}")

        # 获取问卷数据（用于MBTI等信息）
        questionnaire = None
        if corpus.get("questionnaire_id"):
            questionnaire = await get_questionnaire(corpus["questionnaire_id"])

        mbti_type = self._extract_mbti(corpus, questionnaire)
        persona = corpus.get("persona") or {}
        anchors = corpus.get("anchors") or []
        bridges = corpus.get("bridges") or []
        vocabulary = corpus.get("vocabulary") or []
        patterns = corpus.get("patterns") or []
        band_strategy = corpus.get("band_strategy") or {}
        user_style = corpus.get("user_style") or {}

        # 构建 Markdown 内容
        sections = []

        # 标题
        sections.append(f"# PersonaLingo Skill - {mbti_type}")

        # 语料库生成流程
        sections.append("""## 语料库生成流程

### 输入
- MBTI类型 + 兴趣问卷 + 目标分数

### 流程
1. **用户画像生成** → MBTI维度分析 + 沟通风格推断
2. **锚点故事生成** → 3-4个个人核心故事
3. **题库桥接** → 21题桥接法连接锚点和题库
4. **词汇升级** → 分数段适配的词汇表
5. **句型模板** → MBTI匹配的表达模式

### 输出
- 完整个性化语料库""")

        # 对话维护流程
        sections.append("""## 对话维护流程

### 输入
- 用户对话 / 上传资料

### 流程
1. **RAG 检索** → 从语料库获取相关上下文
2. **对话回复** → 带教练角色的智能回复
3. **内容提取** → 识别可加入语料库的新素材
4. **风格学习** → 更新用户表达风格统计
5. **语料融合** → 确认后更新语料库

### 输出
- 更新后的语料库 + 学习笔记""")

        # 当前语料库摘要
        target_score = band_strategy.get("target_score", "N/A") if isinstance(band_strategy, dict) else "N/A"
        sections.append(f"""## 当前语料库摘要
- 锚点数: {len(anchors)}
- 桥接数: {len(bridges)}
- 词汇数: {len(vocabulary)}
- 句型数: {len(patterns)}
- 目标分数: {target_score}""")

        # 用户风格特征
        avg_sentence_len = user_style.get("avg_sentence_length", "N/A")
        connectors = ", ".join(user_style.get("frequent_connectors", [])) or "N/A"
        vocab_level = user_style.get("vocabulary_level", "N/A")
        sections.append(f"""## 用户风格特征
- MBTI类型: {mbti_type}
- 平均句长: {avg_sentence_len} words
- 常用连接词: {connectors}
- 词汇层级: {vocab_level}""")

        # 锚点故事概览
        if anchors:
            anchor_lines = ["## 锚点故事概览"]
            for i, anchor in enumerate(anchors, 1):
                label = anchor.get("label", f"锚点{i}")
                keywords = ", ".join(anchor.get("keywords", []))
                anchor_lines.append(f"- **{label}**: {keywords}")
            sections.append("\n".join(anchor_lines))

        return "\n\n".join(sections)

    async def export_json(self, corpus_id: str) -> dict:
        """
        导出 JSON 格式 Skill 文件
        返回结构化的工作流描述 + 语料库摘要
        """
        corpus = await get_corpus(corpus_id)
        if not corpus:
            raise ValueError(f"语料库不存在: {corpus_id}")

        # 获取问卷数据
        questionnaire = None
        if corpus.get("questionnaire_id"):
            questionnaire = await get_questionnaire(corpus["questionnaire_id"])

        mbti_type = self._extract_mbti(corpus, questionnaire)
        persona = corpus.get("persona") or {}
        anchors = corpus.get("anchors") or []
        bridges = corpus.get("bridges") or []
        vocabulary = corpus.get("vocabulary") or []
        patterns = corpus.get("patterns") or []
        band_strategy = corpus.get("band_strategy") or {}
        user_style = corpus.get("user_style") or {}

        target_score = band_strategy.get("target_score", "6.5") if isinstance(band_strategy, dict) else "6.5"

        result = {
            "skill_name": "PersonaLingo",
            "version": "2.0",
            "user_profile": {
                "mbti_type": mbti_type,
                "interests": persona.get("interests", []),
                "communication_style": persona.get("communication_style", ""),
            },
            "workflows": [
                {
                    "name": "corpus_generation",
                    "description": "语料库生成流程",
                    "steps": [
                        {
                            "step": 1,
                            "name": "persona",
                            "description": "用户画像生成",
                            "input": {"mbti_type": "str", "interests": "list", "target_score": "str"},
                            "output": {"persona_profile": "dict", "communication_style": "str"},
                        },
                        {
                            "step": 2,
                            "name": "anchors",
                            "description": "锚点故事生成",
                            "input": {"persona_profile": "dict"},
                            "output": {"anchor_stories": "list[3-4]"},
                        },
                        {
                            "step": 3,
                            "name": "bridges",
                            "description": "题库桥接",
                            "input": {"anchors": "list", "topic_pool": "list"},
                            "output": {"bridge_responses": "list"},
                        },
                        {
                            "step": 4,
                            "name": "vocabulary",
                            "description": "词汇升级",
                            "input": {"target_score": "str", "interests": "list"},
                            "output": {"vocabulary_upgrades": "list[25-30]"},
                        },
                        {
                            "step": 5,
                            "name": "patterns",
                            "description": "句型模板",
                            "input": {"mbti_type": "str", "target_score": "str"},
                            "output": {"sentence_patterns": "list[8-10]"},
                        },
                    ],
                },
                {
                    "name": "conversation_maintenance",
                    "description": "对话维护流程",
                    "steps": [
                        {
                            "step": 1,
                            "name": "rag_retrieval",
                            "description": "RAG 检索",
                            "input": {"user_message": "str", "corpus_id": "str"},
                            "output": {"relevant_context": "list"},
                        },
                        {
                            "step": 2,
                            "name": "coach_reply",
                            "description": "对话回复",
                            "input": {"context": "list", "user_message": "str"},
                            "output": {"reply": "str"},
                        },
                        {
                            "step": 3,
                            "name": "content_extraction",
                            "description": "内容提取",
                            "input": {"conversation": "list"},
                            "output": {"new_materials": "list"},
                        },
                        {
                            "step": 4,
                            "name": "style_learning",
                            "description": "风格学习",
                            "input": {"user_messages": "list"},
                            "output": {"style_stats": "dict"},
                        },
                        {
                            "step": 5,
                            "name": "corpus_merge",
                            "description": "语料融合",
                            "input": {"new_materials": "list", "corpus_id": "str"},
                            "output": {"updated_corpus": "dict"},
                        },
                    ],
                },
            ],
            "corpus_summary": {
                "anchors_count": len(anchors),
                "bridges_count": len(bridges),
                "vocabulary_count": len(vocabulary),
                "patterns_count": len(patterns),
                "band_target": target_score,
            },
            "user_style": {
                "avg_sentence_length": user_style.get("avg_sentence_length"),
                "frequent_connectors": user_style.get("frequent_connectors", []),
                "vocabulary_level": user_style.get("vocabulary_level"),
            },
            "export_time": datetime.now().isoformat(),
        }

        return result

    def _extract_mbti(self, corpus: dict, questionnaire: dict | None) -> str:
        """从语料库或问卷中提取 MBTI 类型"""
        # 优先从 persona 中获取
        persona = corpus.get("persona") or {}
        if persona.get("mbti_type"):
            return persona["mbti_type"]
        # 然后从问卷中获取
        if questionnaire and questionnaire.get("mbti_type"):
            return questionnaire["mbti_type"]
        return "Unknown"

    # ============================================================
    # Runnable Skill Pack (三段式蒸馏的自包含可运行产物)
    # ============================================================

    async def export_runnable_skill(
        self,
        corpus_id: str,
        out_root: Optional[Path] = None,
    ) -> Path:
        """
        导出自包含可运行 Skill 包。

        产物目录:
            <out_root>/<corpus_id>/
              ├── Skill.md               人读用说明 + 7 步链路
              ├── corpus.json            完整语料 + learner_profile + capability_framework
              ├── runtime_protocol.md    Agent 执行协议
              └── prompts/
                   └── README.md         prompts 位置索引

        Args:
            corpus_id: 目标语料库 ID
            out_root: 输出根路径,留空则使用 settings.SKILL_RUNNABLE_OUT_ROOT
                     再降级到 <PersonaLingo>/skills/runnable/

        Returns:
            Path: 导出后的 Skill 包根目录
        """
        corpus = await get_corpus(corpus_id)
        if not corpus:
            raise ValueError(f"语料库不存在: {corpus_id}")

        questionnaire = None
        if corpus.get("questionnaire_id"):
            questionnaire = await get_questionnaire(corpus["questionnaire_id"])

        target_dir = self._resolve_runnable_dir(corpus_id, out_root)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "prompts").mkdir(parents=True, exist_ok=True)

        # 1) Skill.md
        skill_md = await self._build_runnable_md(corpus, questionnaire)
        (target_dir / "Skill.md").write_text(skill_md, encoding="utf-8")

        # 2) corpus.json (完整数据,便于外部 Agent 独立加载)
        corpus_payload = self._build_corpus_payload(corpus, questionnaire)
        (target_dir / "corpus.json").write_text(
            json.dumps(corpus_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # 3) runtime_protocol.md (Agent 执行协议)
        (target_dir / "runtime_protocol.md").write_text(
            self._build_runtime_protocol(corpus_id), encoding="utf-8"
        )

        # 4) prompts/README.md (指向仓库中的 prompt 源文件)
        (target_dir / "prompts" / "README.md").write_text(
            self._build_prompts_index(), encoding="utf-8"
        )

        logger.info(f"[SkillExporter] runnable skill exported to {target_dir}")
        return target_dir

    @staticmethod
    def _resolve_runnable_dir(corpus_id: str, out_root: Optional[Path]) -> Path:
        """统一的路径解析: 显式传入 > env 配置 > 项目默认"""
        if out_root is not None:
            return Path(out_root) / corpus_id
        configured = (get_settings().SKILL_RUNNABLE_OUT_ROOT or "").strip()
        if configured:
            return Path(configured) / corpus_id
        # 项目默认: <PersonaLingo>/skills/runnable/<corpus_id>/
        # __file__ = <repo>/PersonaLingo/backend/app/services/skill_exporter.py
        # parents[3] = <repo>/PersonaLingo
        repo_root = Path(__file__).resolve().parents[3]
        return repo_root / "skills" / "runnable" / corpus_id

    async def _build_runnable_md(self, corpus: dict, questionnaire: Optional[dict]) -> str:
        mbti = self._extract_mbti(corpus, questionnaire)
        anchors = corpus.get("anchors") or []
        vocabulary = corpus.get("vocabulary") or []
        patterns = corpus.get("patterns") or []
        bridges = corpus.get("bridges") or []
        band = corpus.get("band_strategy") or {}
        target_score = band.get("target_score", "N/A") if isinstance(band, dict) else "N/A"
        has_research = bool(corpus.get("learner_profile"))
        has_framework = bool(corpus.get("capability_framework"))

        lines = [
            f"# PersonaLingo Skill - {mbti}",
            "",
            "## 语料库生成流程 (三段式蒸馏 / 7 步)",
            "",
            "### 输入",
            "- MBTI类型 + 兴趣问卷 + 目标分数 (+ 上传材料/对话历史)",
            "",
            "### 流程",
            "1. **Research 深度调研** → 聚合问卷+材料+对话→ LearnerProfile",
            "2. **Framework 框架提炼** → 能力×场景×目标三维矩阵 + 痛点 + 提升路径",
            "3. **Persona 用户画像** → MBTI维度分析 + 沟通风格推断",
            "4. **Anchors 锚点故事** → 3-4个个人核心故事",
            "5. **Bridges 题库桥接** → 21题桥接法连接锚点和题库",
            "6. **Vocabulary 词汇升级** → 分数段适配的词汇表",
            "7. **Patterns 句型模板** → MBTI匹配的表达模式",
            "",
            "### 输出",
            "- 完整个性化语料库 (corpus.json) + 本 Skill.md",
            "",
            "## 当前语料库摘要",
            f"- Stage 1 深度调研产物: {'✓ 已生成' if has_research else '✗ 未启用'}",
            f"- Stage 2 能力框架产物: {'✓ 已生成' if has_framework else '✗ 未启用'}",
            f"- 锚点数: {len(anchors)}",
            f"- 桥接数: {len(bridges)}",
            f"- 词汇数: {len(vocabulary)}",
            f"- 句型数: {len(patterns)}",
            f"- 目标分数: {target_score}",
            "",
            "## 如何加载本 Skill (给外部 Agent)",
            "1. 读取同目录的 `corpus.json` 获得完整语料 + profile + framework",
            "2. 按 `runtime_protocol.md` 描述的协议Call 法执行 RAG 检索 / 生成回复",
            "3. 若需再生成: 调用 PersonaLingo `/api/distill/run?questionnaire_id=<id>`",
        ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def _build_corpus_payload(corpus: dict, questionnaire: Optional[dict]) -> dict:
        """将 DB 记录打包为自包含 JSON(去除 SQLite 内部时间戳等不必要字段)"""
        whitelist = [
            "id", "questionnaire_id", "status",
            "persona", "anchors", "bridges", "vocabulary", "patterns",
            "practices", "band_strategy", "user_style",
            "learner_profile", "capability_framework",
        ]
        payload = {k: corpus.get(k) for k in whitelist if k in corpus}
        payload["questionnaire"] = (
            {
                "mbti_type": questionnaire.get("mbti_type"),
                "interests_tags": questionnaire.get("interests_tags"),
                "ielts_target_score": questionnaire.get("ielts_target_score"),
                "ielts_topic_types": questionnaire.get("ielts_topic_types"),
            }
            if questionnaire
            else None
        )
        payload["skill_manifest"] = {
            "name": "PersonaLingo",
            "version": "3.0",
            "pipeline": "three_stage_distill",
            "stages": [
                "research", "framework",
                "persona", "anchors", "bridges", "vocabulary", "patterns",
            ],
            "exported_at": datetime.now().isoformat(),
        }
        return payload

    @staticmethod
    def _build_runtime_protocol(corpus_id: str) -> str:
        return (
            "# Runtime Protocol (PersonaLingo Skill)\n"
            "\n"
            "本文档描述 Agent 如何加载与调用本 Skill 包。\n"
            "\n"
            "## 1. 入口\n"
            "本 Skill 适配 huashu-nuwa 的两种入口:\n"
            "- **明确目标**: 用户已完成 MBTI 问卷 + 目标分数 → 直接调用 `/api/distill/run`\n"
            "- **模糊需求**: 用户仅提供自由文本 → 先调 `/api/distill/diagnose` 获得诊断问卷,再提交问卷之后进入 run\n"
            "\n"
            "## 2. 数据加载\n"
            "```python\n"
            "import json\n"
            "with open('corpus.json', 'r', encoding='utf-8') as f:\n"
            "    skill = json.load(f)\n"
            "profile  = skill.get('learner_profile') or {}\n"
            "framework = skill.get('capability_framework') or {}\n"
            "anchors  = skill.get('anchors') or []\n"
            "```\n"
            "\n"
            "## 3. 调用菜单 (HTTP)\n"
            "| 操作 | 端点 | 备注 |\n"
            "|---|---|---|\n"
            f"| 对话维护 | `POST /api/conversations/{corpus_id}/chat` | NotebookLM 风格对话 + RAG |\n"
            f"| 查看笔记 | `GET /api/notes/{corpus_id}` | 学习笔记时间线 |\n"
            f"| 重新蒸馏 | `POST /api/distill/run?questionnaire_id=<qid>` | 触发 7 步链路 |\n"
            "\n"
            "## 4. 安全约束\n"
            "- 回答必须以 `corpus.anchors` / `corpus.bridges` / `corpus.vocabulary` 为首要上下文\n"
            "- 不得虚构用户未出现的个人经历\n"
            "- 若 `capability_framework.lift_paths` 给出步骤,教练回复应对齐步骤\n"
        )

    @staticmethod
    def _build_prompts_index() -> str:
        return (
            "# Prompts Index\n"
            "\n"
            "本 Skill 的运行时 prompt 模板集中维护在仓库代码仓(不随包导出以保持可维护性):\n"
            "\n"
            "| Stage | 文件 | 符号 |\n"
            "|---|---|---|\n"
            "| Stage 2 框架提炼 | `backend/app/services/capability_framework.py` | `FRAMEWORK_SYSTEM`, `FRAMEWORK_USER` |\n"
            "| Stage 3 语料生成 | `backend/app/services/corpus_generator_prompts.py` | `PERSONA_*`, `ANCHORS_*`, `BRIDGES_*`, `VOCABULARY_*`, `PATTERNS_*`, `PRACTICES_*` |\n"
            "| QMD 检索 | `backend/app/services/qmd_engine.py` | `QUERY_EXPANSION_PROMPT` |\n"
            "\n"
            "若需内联 prompt,可覆写本目录下的 `stage3_persona.txt` 等文件;Skill 加载会优先采用本地文件。\n"
        )
