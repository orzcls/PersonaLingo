"""
Stage 2 — CapabilityFramework (框架提炼层)

对齐 huashu-nuwa 的"思维框架提炼"段:
从 LearnerProfile 抽象出「能力 × 场景 × 目标」三维矩阵 + 痛点 + 提升路径,
供 Stage 3 的 5 步语料生成作为全局上下文。

实现策略:
- 优先 LLM 一次性 JSON 生成(低温度)
- LLM 不可用/返回非法 JSON → 降级为规则兜底,保证字段非空
"""
import json
import logging
from typing import Optional

from app.services.llm_adapter import get_llm

logger = logging.getLogger(__name__)


FRAMEWORK_SYSTEM = """You are a learning-capability architect for IELTS speaking training.

Given a LearnerProfile (JSON), distill a **CapabilityFramework** with three dimensions:
- ability:  lexical_range, fluency, grammatical_range, pronunciation (+ others if relevant)
- scenario: IELTS parts (P1/P2/P3) and priority topics
- goal:     measurable learning objectives derived from target_score / priority_parts

Also output:
- pain_points: concrete weaknesses with supporting signals from the profile
- lift_paths:  step-by-step improvement plans from current level → target

Rules:
1. Output STRICT JSON only, no prose.
2. Every dimension array MUST be non-empty (at least 1 item).
3. Ground every claim in the profile; do NOT invent facts.
"""

FRAMEWORK_USER = """LearnerProfile:
```json
{profile_json}
```

Respond with this JSON schema:
{{
  "dimensions": {{
    "ability":  [ {{"name": "lexical_range", "current": "6.0", "target": "6.5", "notes": "..."}} ],
    "scenario": [ {{"part": "P1", "topics": ["..."], "priority": "high"}} ],
    "goal":     [ {{"key": "target_score", "value": "6.5"}} ]
  }},
  "pain_points": [ {{"id": "pp1", "desc": "...", "signals": ["..."]}} ],
  "lift_paths":  [ {{"from": "6.0", "to": "6.5", "steps": ["..."]}} ]
}}"""


class CapabilityFramework:
    """Stage 2 能力框架提炼器"""

    def __init__(self):
        self.llm = get_llm()

    async def distill(self, learner_profile: dict) -> dict:
        """LearnerProfile → CapabilityFramework"""
        if not isinstance(learner_profile, dict):
            logger.warning("CapabilityFramework: profile is not a dict, fallback")
            return self._fallback(None)

        # 尝试 LLM
        try:
            return await self._llm_distill(learner_profile)
        except Exception as e:
            logger.warning(f"CapabilityFramework LLM distill failed: {e}; fallback to rule-based")
            return self._fallback(learner_profile)

    # ------------------------ LLM path ------------------------

    async def _llm_distill(self, profile: dict) -> dict:
        # 仅发送摘要避免 prompt 过大
        slim = self._slim_profile(profile)
        prompt = FRAMEWORK_USER.format(profile_json=json.dumps(slim, ensure_ascii=False, indent=2))

        content = await self.llm.chat(
            messages=[
                {"role": "system", "content": FRAMEWORK_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        data = self._safe_json(content)
        if not data or not isinstance(data, dict):
            raise ValueError("LLM returned non-JSON content")
        # 保底填充缺失字段
        return self._merge_with_fallback(data, profile)

    @staticmethod
    def _slim_profile(profile: dict) -> dict:
        """为 LLM 输入瘦身:只保留结构性字段,样本截断"""
        samples = profile.get("language_samples", []) or []
        slim_samples = [
            {"source": s.get("source"), "text": (s.get("text") or "")[:400]}
            for s in samples[:5]
        ]
        return {
            "background": profile.get("background", {}),
            "goal_vector": profile.get("goal_vector", {}),
            "weakness_signals": profile.get("weakness_signals", []),
            "topic_signals": profile.get("topic_signals", {}),
            "source_stats": profile.get("source_stats", {}),
            "language_samples": slim_samples,
        }

    @staticmethod
    def _safe_json(text: str) -> Optional[dict]:
        """容忍 LLM 返回包含 ```json ... ``` 包裹的情况"""
        if not text:
            return None
        t = text.strip()
        # 去除代码块
        if t.startswith("```"):
            lines = [ln for ln in t.splitlines() if not ln.strip().startswith("```")]
            t = "\n".join(lines).strip()
        # 尝试定位第一个 { 和最后一个 }
        start = t.find("{")
        end = t.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(t[start : end + 1])
        except json.JSONDecodeError:
            return None

    # ----------------------- Rule fallback --------------------

    def _fallback(self, profile: Optional[dict]) -> dict:
        """无 LLM / LLM 失败 → 按规则构造最小可用框架"""
        profile = profile or {}
        goal = profile.get("goal_vector", {}) or {}
        weakness = profile.get("weakness_signals", []) or []
        focus_topics = (goal.get("focus_topics") or [])[:6]
        priority_parts = goal.get("priority_parts") or ["P1", "P2"]
        target = str(goal.get("target_score") or "6.5")

        try:
            current = str(round(max(float(target) - 0.5, 5.0), 1))
        except (TypeError, ValueError):
            current = "6.0"

        ability_items = [
            {"name": "lexical_range", "current": current, "target": target,
             "notes": "vocabulary upgrade for target band"},
            {"name": "fluency", "current": current, "target": target,
             "notes": "increase sentence length and connectors"},
            {"name": "grammatical_range", "current": current, "target": target,
             "notes": "mix simple + complex sentences"},
        ]
        scenario_items = [
            {"part": p, "topics": focus_topics, "priority": "high" if i == 0 else "medium"}
            for i, p in enumerate(priority_parts)
        ] or [{"part": "P1", "topics": [], "priority": "high"}]

        goal_items = [
            {"key": "target_score", "value": target},
            {"key": "priority_parts", "value": ",".join(priority_parts)},
        ]
        if goal.get("exam_date"):
            goal_items.append({"key": "exam_date", "value": goal.get("exam_date")})

        pain_points = []
        for idx, sig in enumerate(weakness, 1):
            pain_points.append(
                {
                    "id": f"pp{idx}",
                    "desc": self._humanize_signal(sig),
                    "signals": [sig],
                }
            )
        if not pain_points:
            pain_points.append(
                {
                    "id": "pp0",
                    "desc": "No weakness signals detected; build baseline anchors first.",
                    "signals": [],
                }
            )

        lift_paths = [
            {
                "from": current,
                "to": target,
                "steps": [
                    "Build 3-4 personal anchor stories covering priority topics",
                    "Upgrade 25-30 high-impact vocabulary items aligned to target band",
                    "Drill 8-10 sentence patterns matching communication style",
                    "Practice P2 2-minute monologues with safe-stop checkpoints",
                ],
            }
        ]

        return {
            "dimensions": {
                "ability": ability_items,
                "scenario": scenario_items,
                "goal": goal_items,
            },
            "pain_points": pain_points,
            "lift_paths": lift_paths,
            "source": "rule_fallback",
        }

    def _merge_with_fallback(self, llm_data: dict, profile: dict) -> dict:
        """LLM 数据不完整时用规则兜底填补空位"""
        fb = self._fallback(profile)
        dims = llm_data.get("dimensions") or {}
        merged_dims = {
            "ability": dims.get("ability") or fb["dimensions"]["ability"],
            "scenario": dims.get("scenario") or fb["dimensions"]["scenario"],
            "goal": dims.get("goal") or fb["dimensions"]["goal"],
        }
        return {
            "dimensions": merged_dims,
            "pain_points": llm_data.get("pain_points") or fb["pain_points"],
            "lift_paths": llm_data.get("lift_paths") or fb["lift_paths"],
            "source": "llm",
        }

    @staticmethod
    def _humanize_signal(signal: str) -> str:
        if signal.startswith("short_sentences"):
            return "Sentences are too short; needs longer clauses with subordinators."
        if signal == "lack_connectors":
            return "Few discourse connectors; needs logical linking words."
        if signal.startswith("low_lexical_diversity"):
            return "Lexical diversity is low; needs vocabulary upgrade."
        return f"Weakness detected: {signal}"


# 模块级工厂
_framework_instance: Optional[CapabilityFramework] = None


def get_capability_framework() -> CapabilityFramework:
    global _framework_instance
    if _framework_instance is None:
        _framework_instance = CapabilityFramework()
    return _framework_instance
