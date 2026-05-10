"""
语料生成引擎 - LLM 驱动5步生成 + 分数段策略
完整流程: Persona → Anchors → Bridges → Vocabulary → Patterns (+ Practices)
"""
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional

from app.services.llm_adapter import get_llm
from app.services.corpus_rag import get_corpus_rag
from app.services.learner_researcher import get_learner_researcher
from app.services.capability_framework import get_capability_framework
from app.db.crud import (
    get_questionnaire, create_corpus, update_corpus, get_corpus, get_topics
)
from app.services.corpus_generator_prompts import (
    PERSONA_SYSTEM, PERSONA_USER,
    ANCHORS_SYSTEM, ANCHORS_USER,
    BRIDGES_SYSTEM, BRIDGES_USER,
    VOCABULARY_SYSTEM, VOCABULARY_USER,
    PATTERNS_SYSTEM, PATTERNS_USER,
    PRACTICES_SYSTEM, PRACTICES_USER,
)

logger = logging.getLogger(__name__)

# 加载分数段策略
_DATA_DIR = Path(__file__).parent.parent / "data"
_BAND_STRATEGIES_PATH = _DATA_DIR / "band_strategies.json"
_band_strategies_cache: Optional[dict] = None

# 加载内置地道词汇和题型数据
_IDIOMATIC_VOCAB_PATH = _DATA_DIR / "idiomatic_vocabulary.json"
_QUESTION_TYPES_PATH = _DATA_DIR / "question_types.json"
_PRACTICE_EXAMPLES_PATH = _DATA_DIR / "practice_examples.json"
_idiomatic_vocab_cache: Optional[dict] = None
_question_types_cache: Optional[dict] = None
_practice_examples_cache: Optional[dict] = None


def _load_band_strategies() -> dict:
    global _band_strategies_cache
    if _band_strategies_cache is None:
        with open(_BAND_STRATEGIES_PATH, "r", encoding="utf-8") as f:
            _band_strategies_cache = json.load(f)
    return _band_strategies_cache


def _get_band_strategy(target_score: str) -> dict:
    """获取对应分数段策略，默认6.5"""
    strategies = _load_band_strategies()
    # 规范化分数字符串
    score = str(target_score).strip()
    if score in strategies:
        return strategies[score]
    # 尝试匹配最接近的
    for key in ["6.5", "6.0", "7.0", "7.5"]:
        if key in strategies:
            return strategies[key]
    return strategies.get("6.5", {})


def _load_idiomatic_vocabulary() -> dict:
    """加载内置地道词汇表"""
    global _idiomatic_vocab_cache
    if _idiomatic_vocab_cache is None:
        if _IDIOMATIC_VOCAB_PATH.exists():
            with open(_IDIOMATIC_VOCAB_PATH, "r", encoding="utf-8") as f:
                _idiomatic_vocab_cache = json.load(f)
        else:
            _idiomatic_vocab_cache = {}
    return _idiomatic_vocab_cache


def _load_question_types() -> dict:
    """加载题型分类数据"""
    global _question_types_cache
    if _question_types_cache is None:
        if _QUESTION_TYPES_PATH.exists():
            with open(_QUESTION_TYPES_PATH, "r", encoding="utf-8") as f:
                _question_types_cache = json.load(f)
        else:
            _question_types_cache = {}
    return _question_types_cache


def _load_practice_examples() -> dict:
    """加载练习范例数据"""
    global _practice_examples_cache
    if _practice_examples_cache is None:
        if _PRACTICE_EXAMPLES_PATH.exists():
            with open(_PRACTICE_EXAMPLES_PATH, "r", encoding="utf-8") as f:
                _practice_examples_cache = json.load(f)
        else:
            _practice_examples_cache = {}
    return _practice_examples_cache


def _get_idiomatic_words_for_band(target_score: str, topics: list[str] = None) -> list[dict]:
    """根据分数段和话题筛选适合的地道词汇"""
    vocab_data = _load_idiomatic_vocabulary()
    if not vocab_data or "categories" not in vocab_data:
        return []

    score = float(target_score) if target_score else 6.5
    result = []
    for category in vocab_data["categories"]:
        for word in category.get("words", []):
            band = word.get("band_level", "6.0+")
            band_num = float(band.replace("+", ""))
            if band_num <= score + 0.5:  # 允许略高于目标分的词汇
                if topics:
                    word_topics = word.get("usage_topics", [])
                    if any(t.lower() in [wt.lower() for wt in word_topics] for t in topics):
                        result.append({**word, "source_category": category["category"]})
                else:
                    result.append({**word, "source_category": category["category"]})
    return result[:30]  # 限制数量避免 prompt 过长


def _get_question_type_info(question: str) -> dict:
    """根据问题内容匹配题型分类信息"""
    qt_data = _load_question_types()
    if not qt_data or "question_types" not in qt_data:
        return {}

    q_lower = question.lower()
    for qt in qt_data["question_types"]:
        # 简单关键词匹配
        if qt["type"] == "preference" and any(kw in q_lower for kw in ["do you like", "favorite", "do you enjoy", "do you want"]):
            return qt
        elif qt["type"] == "comparison" and any(kw in q_lower for kw in ["prefer", " or ", "which do you"]):
            return qt
        elif qt["type"] == "category" and any(kw in q_lower for kw in ["what kind", "what kinds", "what type"]):
            return qt
        elif qt["type"] == "opinion" and any(kw in q_lower for kw in ["do you think", "should", "is it important"]):
            return qt
        elif qt["type"] == "experience" and any(kw in q_lower for kw in ["have you ever", "last time", "did you", "when did"]):
            return qt
    return {}


def _parse_json_response(text: str) -> any:
    """从 LLM 响应中提取 JSON，容错处理"""
    # 尝试直接解析
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试提取 ```json ... ``` 代码块
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        try:
            return json.loads(text[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass
    # 尝试提取 ``` ... ``` 代码块
    if "```" in text:
        parts = text.split("```")
        for part in parts[1::2]:  # 奇数索引为代码块内容
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue
    # 尝试找到第一个 [ 或 { 到最后一个 ] 或 }
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        start_idx = text.find(start_char)
        end_idx = text.rfind(end_char)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                return json.loads(text[start_idx:end_idx + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"Failed to parse JSON from LLM response: {text[:200]}...")


# 进度状态存储（内存级，供 SSE 读取）
_generation_progress: dict[str, dict] = {}


def get_generation_progress(corpus_id: str) -> dict:
    """获取生成进度"""
    return _generation_progress.get(corpus_id, {"status": "unknown", "steps": {}})


def set_generation_progress(corpus_id: str, step: str, status: str, data: any = None, questionnaire_id: str = None):
    """更新生成进度"""
    if corpus_id not in _generation_progress:
        _generation_progress[corpus_id] = {"status": "generating", "steps": {}, "questionnaire_id": questionnaire_id}
    _generation_progress[corpus_id]["steps"][step] = {
        "status": status,
        "data": data
    }
    if status == "failed":
        _generation_progress[corpus_id]["status"] = "failed"


def find_progress_by_questionnaire(questionnaire_id: str) -> tuple[str | None, dict | None]:
    """通过 questionnaire_id 查找对应的 corpus_id 和进度"""
    for corpus_id, progress in _generation_progress.items():
        if progress.get("questionnaire_id") == questionnaire_id:
            return corpus_id, progress
    return None, None


class CorpusGenerator:
    """LLM 驱动的5步语料生成引擎"""

    def __init__(self):
        self.llm = get_llm()

    async def generate_full_corpus(self, questionnaire_id: str, include_research: bool = True) -> str:
        """
        完整 7 步生成流程(三段式蒸馏),返回 corpus_id
        每步完成后立即写入数据库,防止中途失败丢失
    
        Args:
            questionnaire_id: 问卷 ID
            include_research: 是否启用 Stage 1+2(深度调研+框架提炼)
                              默认 True;旧链路或测试可传 False 回退到 5 步
        """
        # 1. 获取问卷数据
        questionnaire = await get_questionnaire(questionnaire_id)
        if not questionnaire:
            raise ValueError(f"Questionnaire not found: {questionnaire_id}")
    
        # 2. 获取分数段策略
        target_score = questionnaire.get("ielts_target_score", "6.5")
        band_strategy = _get_band_strategy(target_score)
    
        # 3. 创建 corpus 记录
        corpus_id = await create_corpus(questionnaire_id)
        await update_corpus(corpus_id, {
            "band_strategy": band_strategy,
            "status": "generating"
        })
    
        _generation_progress[corpus_id] = {"status": "generating", "steps": {}, "questionnaire_id": questionnaire_id}
    
        try:
            # Stage 1 深度调研 + Stage 2 框架提炼(失败降级,不阻断主流程)
            if include_research:
                try:
                    set_generation_progress(corpus_id, "research", "generating")
                    researcher = get_learner_researcher()
                    learner_profile = await researcher.research(questionnaire_id, corpus_id)
                    await update_corpus(corpus_id, {"learner_profile": learner_profile})
                    set_generation_progress(corpus_id, "research", "completed", learner_profile)
    
                    set_generation_progress(corpus_id, "framework", "generating")
                    framework = get_capability_framework()
                    capability = await framework.distill(learner_profile)
                    await update_corpus(corpus_id, {"capability_framework": capability})
                    set_generation_progress(corpus_id, "framework", "completed", capability)
                except Exception as stage12_err:
                    logger.warning(
                        f"Stage 1/2 failed for {corpus_id}, fallback to legacy 5-step: {stage12_err}"
                    )
                    set_generation_progress(corpus_id, "research", "skipped")
                    set_generation_progress(corpus_id, "framework", "skipped")
    
            # Step 1: 生成用户画像
            set_generation_progress(corpus_id, "persona", "generating")
            persona = await self.generate_persona(questionnaire, band_strategy)
            await update_corpus(corpus_id, {"persona": persona})
            set_generation_progress(corpus_id, "persona", "completed", persona)

            # Step 2: 生成锚点故事
            set_generation_progress(corpus_id, "anchors", "generating")
            anchors = await self.generate_anchors(persona, band_strategy)
            await update_corpus(corpus_id, {"anchors": anchors})
            set_generation_progress(corpus_id, "anchors", "completed", anchors)

            # Step 3: 生成桥接策略
            set_generation_progress(corpus_id, "bridges", "generating")
            topics = await self._load_topics()
            bridges = await self.generate_bridges(anchors, topics, band_strategy)
            await update_corpus(corpus_id, {"bridges": bridges})
            set_generation_progress(corpus_id, "bridges", "completed", bridges)

            # Step 4: 生成词汇升级
            set_generation_progress(corpus_id, "vocabulary", "generating")
            vocabulary = await self.generate_vocabulary(persona, anchors, band_strategy)
            await update_corpus(corpus_id, {"vocabulary": vocabulary})
            set_generation_progress(corpus_id, "vocabulary", "completed", vocabulary)

            # Step 5: 生成句型模板
            set_generation_progress(corpus_id, "patterns", "generating")
            patterns = await self.generate_patterns(persona, band_strategy)
            await update_corpus(corpus_id, {"patterns": patterns})
            set_generation_progress(corpus_id, "patterns", "completed", patterns)

            # Bonus: 生成练习设计
            set_generation_progress(corpus_id, "practices", "generating")
            practices = await self.generate_practices(persona, anchors, bridges, band_strategy)
            await update_corpus(corpus_id, {"practices": practices})
            set_generation_progress(corpus_id, "practices", "completed", practices)

            # 标记完成
            await update_corpus(corpus_id, {"status": "completed"})
            _generation_progress[corpus_id]["status"] = "completed"

            # 建立 RAG 索引
            rag = get_corpus_rag()
            await rag.index_corpus(corpus_id)

            # 语料库生成完成后自动触发笔记生成（后台任务，失败不阻断主流程）
            try:
                from app.services.note_generator import get_note_generator
                note_gen = get_note_generator()
                asyncio.create_task(note_gen.generate_after_corpus_creation(corpus_id))
            except Exception as note_err:
                logger.warning(f"Auto-trigger note generation failed for {corpus_id}: {note_err}")

        except Exception as e:
            logger.error(f"Corpus generation failed for {corpus_id}: {e}", exc_info=True)
            await update_corpus(corpus_id, {"status": "failed"})
            _generation_progress[corpus_id]["status"] = "failed"
            _generation_progress[corpus_id]["error"] = str(e)
            raise

        return corpus_id

    async def generate_persona(self, questionnaire: dict, band_strategy: dict) -> dict:
        """Step 1: MBTI + 兴趣 + 个人背景 + 真实经历 → 用户画像"""
        # 解析问卷字段
        mbti_type = questionnaire.get("mbti_type", "INFP")
        mbti_dimensions = questionnaire.get("mbti_dimensions", {})
        if isinstance(mbti_dimensions, str):
            try:
                mbti_dimensions = json.loads(mbti_dimensions)
            except (json.JSONDecodeError, TypeError):
                mbti_dimensions = {}

        interests_tags = questionnaire.get("interests_tags", [])
        if isinstance(interests_tags, str):
            try:
                interests_tags = json.loads(interests_tags)
            except (json.JSONDecodeError, TypeError):
                interests_tags = []

        interests_descriptions = questionnaire.get("interests_descriptions", [])
        if isinstance(interests_descriptions, str):
            try:
                interests_descriptions = json.loads(interests_descriptions)
            except (json.JSONDecodeError, TypeError):
                interests_descriptions = []

        target_score = questionnaire.get("ielts_target_score", "6.5")

        # 新增字段
        personal_bg = questionnaire.get("personal_background", {}) or {}
        life_exp = questionnaire.get("life_experiences", {}) or {}

        # 构建增强的 persona context
        persona_context = self._build_persona_context(
            mbti_type, interests_tags, interests_descriptions,
            personal_bg, life_exp
        )

        prompt = PERSONA_USER.format(
            mbti_type=mbti_type,
            mbti_dimensions=json.dumps(mbti_dimensions),
            interests_tags=", ".join(interests_tags) if interests_tags else "general",
            interests_descriptions=", ".join(interests_descriptions) if interests_descriptions else "N/A",
            target_score=target_score,
            band_label=band_strategy.get("label", ""),
            vocab_level=band_strategy.get("vocabulary", {}).get("level", "intermediate"),
            grammar_complexity=band_strategy.get("grammar", {}).get("complexity", "compound_complex"),
            fluency_style=band_strategy.get("fluency", {}).get("filler_strategy", ""),
            persona_context=persona_context,
        )

        messages = [
            {"role": "system", "content": PERSONA_SYSTEM},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.chat(messages, temperature=0.7, max_tokens=2048)
        persona = _parse_json_response(response)
        return persona

    def _build_persona_context(self, mbti_type, tags, descriptions, background, experiences):
        """将用户所有维度数据整合为人物画像上下文"""
        context_parts = []

        # 个人背景
        if background:
            bg_text = f"Age: {background.get('age', 'N/A')}, Gender: {background.get('gender', 'N/A')}, "
            bg_text += f"Profession: {background.get('profession', 'N/A')}, City: {background.get('city', 'N/A')}"
            if background.get('zodiac'):
                bg_text += f", Zodiac: {background['zodiac']}"
            if background.get('self_description'):
                bg_text += f"\nSelf-description: {background['self_description']}"
            context_parts.append(f"[Personal Background]\n{bg_text}")

        # 重要的人
        if experiences and experiences.get('people'):
            people_text = "\n".join([
                f"- {p['relationship']}: {p['nickname']} - {p['description']}"
                + (f" ({p['memorable_experience']})" if p.get('memorable_experience') else "")
                for p in experiences['people']
            ])
            context_parts.append(f"[Important People]\n{people_text}")

        # 有意义的物
        if experiences and experiences.get('objects'):
            objects_text = "\n".join([
                f"- {o['category']}: {o['name']} - {o['significance']}"
                for o in experiences['objects']
            ])
            context_parts.append(f"[Meaningful Objects]\n{objects_text}")

        # 印象深刻的地
        if experiences and experiences.get('places'):
            places_text = "\n".join([
                f"- {p['category']}: {p['name']} - {p['experience']}"
                for p in experiences['places']
            ])
            context_parts.append(f"[Memorable Places]\n{places_text}")

        return "\n\n".join(context_parts)

    async def generate_anchors(self, persona: dict, band_strategy: dict) -> list[dict]:
        """Step 2: 生成3-4个个人锚点故事"""
        target_score = persona.get("band_adaptation", {}).get("target", "6.5")
        timing = band_strategy.get("timing", {})

        prompt = ANCHORS_USER.format(
            persona_json=json.dumps(persona, ensure_ascii=False, indent=2),
            target_score=target_score,
            vocab_level=band_strategy.get("vocabulary", {}).get("level", "intermediate"),
            grammar_complexity=band_strategy.get("grammar", {}).get("complexity", "compound_complex"),
            p1_target_seconds=timing.get("p1_target_seconds", 25),
            safe_stop_strategy=timing.get("safe_stop_strategy", "Natural conclusion"),
        )

        messages = [
            {"role": "system", "content": ANCHORS_SYSTEM},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.chat(messages, temperature=0.8, max_tokens=4096)
        anchors = _parse_json_response(response)

        # 确保返回列表
        if isinstance(anchors, dict):
            anchors = anchors.get("anchors", [anchors])
        return anchors

    async def generate_bridges(self, anchors: list, topics: list, band_strategy: dict) -> list[dict]:
        """Step 3: 题库桥接（21题桥接法 + 题型分类参考）"""
        timing = band_strategy.get("timing", {})
        target_score = band_strategy.get("label", "6.5").split(" ")[1] if " " in band_strategy.get("label", "") else "6.5"

        # 选取代表性题目（P1取前10，P2取前5）
        p1_topics = [t for t in topics if t.get("part") == "P1"][:10]
        p2_topics = [t for t in topics if t.get("part") == "P2"][:5]
        selected_topics = p1_topics + p2_topics

        # 简化 topics 信息传给 LLM
        topics_for_prompt = [
            {"id": t["id"], "title": t["title"], "category": t.get("category", ""), "part": t.get("part", "P1")}
            for t in selected_topics
        ]

        # 加载题型分类信息，附加到 prompt 中
        qt_data = _load_question_types()
        question_type_ref = ""
        if qt_data and "question_types" in qt_data:
            question_type_ref = "\n\n## 题型分类参考（请根据题目类型选择对应的回答框架）:\n"
            for qt in qt_data["question_types"]:
                framework = qt.get("answer_framework", {})
                question_type_ref += f"- **{qt['description']}** ({qt['template']}): {framework.get('structure', '')}\n"
                tips = framework.get("tips", [])
                if tips:
                    question_type_ref += f"  技巧: {'; '.join(tips[:3])}\n"

        prompt = BRIDGES_USER.format(
            anchors_json=json.dumps(anchors, ensure_ascii=False, indent=2),
            topics_json=json.dumps(topics_for_prompt, ensure_ascii=False, indent=2),
            target_score=target_score,
            p1_target_seconds=timing.get("p1_target_seconds", 25),
            p1_max_seconds=timing.get("p1_max_seconds", 30),
            safe_stop_strategy=timing.get("safe_stop_strategy", "Natural conclusion"),
            grammar_structures=", ".join(band_strategy.get("grammar", {}).get("structures", [])),
            upgrade_ratio=band_strategy.get("vocabulary", {}).get("upgrade_ratio", 0.35),
            filler_strategy=band_strategy.get("fluency", {}).get("filler_strategy", ""),
        )

        messages = [
            {"role": "system", "content": BRIDGES_SYSTEM},
            {"role": "user", "content": prompt}
        ]

        # 将题型分类参考追加到 prompt
        if question_type_ref:
            messages[-1]["content"] += question_type_ref

        response = await self.llm.chat(messages, temperature=0.7, max_tokens=6000)
        bridges = _parse_json_response(response)

        if isinstance(bridges, dict):
            bridges = bridges.get("bridges", [bridges])
        return bridges

    async def generate_vocabulary(self, persona: dict, anchors: list, band_strategy: dict) -> list[dict]:
        """Step 4: 分数段适配词汇升级（引用内置地道词汇）"""
        vocab_config = band_strategy.get("vocabulary", {})
        upgrade_ratio = vocab_config.get("upgrade_ratio", 0.35)
        target_score = persona.get("band_adaptation", {}).get("target", "6.5")

        # 获取适合该分数段的内置地道词汇
        interest_topics = persona.get("interest_connections", {}).get("primary_themes", [])
        idiomatic_words = _get_idiomatic_words_for_band(target_score, interest_topics)
        idiomatic_ref = ""
        if idiomatic_words:
            idiomatic_ref = "\n\n## 参考地道表达列表（请从中选择适合该用户分数段和话题的词汇融入建议）:\n"
            for w in idiomatic_words:
                idiomatic_ref += f"- {w['word']} ({w['meaning']}): {w.get('example', '')}\n"

        prompt = VOCABULARY_USER.format(
            persona_json=json.dumps(persona, ensure_ascii=False, indent=2),
            anchors_json=json.dumps(anchors, ensure_ascii=False, indent=2),
            target_score=target_score,
            vocab_level=vocab_config.get("level", "intermediate"),
            upgrade_ratio=upgrade_ratio,
            vocab_avoid=", ".join(vocab_config.get("avoid", [])),
            upgrade_count=int(upgrade_ratio * 10),
        )
        prompt += idiomatic_ref

        messages = [
            {"role": "system", "content": VOCABULARY_SYSTEM},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.chat(messages, temperature=0.7, max_tokens=4096)
        vocabulary = _parse_json_response(response)

        if isinstance(vocabulary, dict):
            vocabulary = vocabulary.get("vocabulary", [vocabulary])
        return vocabulary

    async def generate_patterns(self, persona: dict, band_strategy: dict) -> list[dict]:
        """Step 5: MBTI 风格匹配句型模板"""
        grammar_config = band_strategy.get("grammar", {})
        target_score = persona.get("band_adaptation", {}).get("target", "6.5")

        prompt = PATTERNS_USER.format(
            persona_json=json.dumps(persona, ensure_ascii=False, indent=2),
            target_score=target_score,
            grammar_complexity=grammar_config.get("complexity", "compound_complex"),
            grammar_structures=", ".join(grammar_config.get("structures", [])),
            filler_strategy=band_strategy.get("fluency", {}).get("filler_strategy", ""),
        )

        messages = [
            {"role": "system", "content": PATTERNS_SYSTEM},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.chat(messages, temperature=0.7, max_tokens=4096)
        patterns = _parse_json_response(response)

        if isinstance(patterns, dict):
            patterns = patterns.get("patterns", [patterns])
        return patterns

    async def generate_practices(self, persona: dict, anchors: list, bridges: list, band_strategy: dict) -> list[dict]:
        """Bonus Step: 练习设计"""
        timing = band_strategy.get("timing", {})
        target_score = persona.get("band_adaptation", {}).get("target", "6.5")

        # 取前3个 bridges 作为示例
        bridges_sample = bridges[:3] if bridges else []

        prompt = PRACTICES_USER.format(
            persona_json=json.dumps(persona, ensure_ascii=False, indent=2),
            anchors_json=json.dumps(anchors, ensure_ascii=False, indent=2),
            bridges_sample_json=json.dumps(bridges_sample, ensure_ascii=False, indent=2),
            target_score=target_score,
            p1_target_seconds=timing.get("p1_target_seconds", 25),
            safe_stop_strategy=timing.get("safe_stop_strategy", "Natural conclusion"),
        )

        messages = [
            {"role": "system", "content": PRACTICES_SYSTEM},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.chat(messages, temperature=0.8, max_tokens=6000)
        practices = _parse_json_response(response)

        if isinstance(practices, dict):
            practices = practices.get("practices", [practices])
        return practices

    async def _load_topics(self) -> list:
        """加载题库（优先从数据库，否则从文件）"""
        # 先尝试数据库
        topics = await get_topics()
        if topics:
            return topics

        # 回退到文件
        data_dir = Path(__file__).parent.parent / "data"
        all_topics = []
        for filename in ["topics_p1.json", "topics_p2.json"]:
            filepath = data_dir / filename
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    all_topics.extend(json.load(f))
        return all_topics


# 模块级实例获取
_generator_instance: Optional[CorpusGenerator] = None


def get_corpus_generator() -> CorpusGenerator:
    """获取语料生成器单例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CorpusGenerator()
    return _generator_instance
