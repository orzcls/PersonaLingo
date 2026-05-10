"""冒烟脚本:插入最小 corpus + questionnaire → 调 /api/distill/skill/{id}/runnable → 打印结果"""
import asyncio
import json
import sys
import uuid
import urllib.error
import urllib.request
from datetime import datetime

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))

import aiosqlite  # noqa: E402

DB = "app/data/personalingo.db"


async def setup_fixture():
    qid = f"smoke_q_{uuid.uuid4().hex[:8]}"
    cid = f"smoke_c_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    persona = {"mbti": "INTJ", "style": "analytical"}
    anchors = [{"title": "Travel to Japan", "keywords": ["kyoto", "ramen"]}]
    bridges = []
    vocabulary = {"items": ["utilize", "albeit"]}
    patterns = ["It's worth noting that ..."]

    learner_profile = {
        "background": {"mbti": "INTJ", "target_score": 6.5, "exam_timeline": "3 months"},
        "language_samples": [{"source": "conversation", "text": "I like traveling."}],
        "weakness_signals": ["short_sentences:3.5", "lack_connectors"],
        "goal_vector": {"target_score": 6.5},
        "topic_signals": {"hot": ["travel"]},
    }
    capability_framework = {
        "matrix": [{"ability": "fluency", "scenario": "P2 narrative", "goal": "extend to 2min"}],
        "pain_points": ["过短回答"],
        "lift_paths": ["每次回答拓展 2 个细节 + 1 个情绪形容词"],
    }

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """INSERT INTO questionnaires
               (id, mbti_type, mbti_dimensions, interests_tags, interests_descriptions,
                ielts_target_score, ielts_topic_types, ielts_exam_date,
                personal_background, life_experiences, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                qid, "INTJ",
                json.dumps({"I": 0.7, "N": 0.8, "T": 0.9, "J": 0.6}),
                json.dumps(["reading", "travel"]),
                json.dumps({"reading": "I read sci-fi."}),
                "6.5", json.dumps(["P1", "P2"]), "2026-08-01",
                "Undergraduate student, CS major",
                json.dumps(["exchange program in Japan"]),
                now,
            ),
        )
        await db.execute(
            """INSERT INTO corpora
               (id, questionnaire_id, status, persona, anchors, bridges, vocabulary, patterns,
                learner_profile, capability_framework, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                cid, qid, "completed",
                json.dumps(persona, ensure_ascii=False),
                json.dumps(anchors, ensure_ascii=False),
                json.dumps(bridges, ensure_ascii=False),
                json.dumps(vocabulary, ensure_ascii=False),
                json.dumps(patterns, ensure_ascii=False),
                json.dumps(learner_profile, ensure_ascii=False),
                json.dumps(capability_framework, ensure_ascii=False),
                now, now,
            ),
        )
        await db.commit()
    return cid


def call(url: str, method: str = "GET", body=None):
    req = urllib.request.Request(url, method=method)
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        ct = r.headers.get("Content-Type", "")
        raw = r.read()
        return r.status, ct, raw


async def main():
    cid = await setup_fixture()
    print(f"[fixture] corpus_id = {cid}")

    # 1) runnable
    status, ct, raw = call(f"http://localhost:9849/api/distill/skill/{cid}/runnable")
    print(f"[runnable] status={status}")
    print(json.dumps(json.loads(raw), ensure_ascii=False, indent=2)[:800])

    # 2) download (just size)
    status, ct, raw = call(f"http://localhost:9849/api/distill/skill/{cid}/runnable/download")
    print(f"[download] status={status} content-type={ct} bytes={len(raw)}")
    assert status == 200 and ct.startswith("application/zip"), "download 应返回 zip"

    # 3) preview markdown (P2-3)
    status, ct, raw = call(f"http://localhost:9849/api/distill/skill/{cid}/runnable/preview?format=markdown")
    text = raw.decode("utf-8", errors="replace")
    print(f"[preview md] status={status} content-type={ct} bytes={len(raw)}")
    print("  first-line:", text.splitlines()[0][:80] if text else "<empty>")
    assert status == 200 and ct.startswith("text/markdown"), "preview md 应返回 text/markdown"
    assert "# " in text, "Skill.md 应含 markdown 标题"

    # 4) preview html (P2-3)
    status, ct, raw = call(f"http://localhost:9849/api/distill/skill/{cid}/runnable/preview?format=html")
    html = raw.decode("utf-8", errors="replace")
    print(f"[preview html] status={status} content-type={ct} bytes={len(raw)}")
    assert status == 200 and ct.startswith("text/html"), "preview html 应返回 text/html"
    assert "<!doctype html>" in html and "<h1>" in html, "html 应含 doctype 和 h1"

    # 5) 非法 format
    try:
        call(f"http://localhost:9849/api/distill/skill/{cid}/runnable/preview?format=pdf")
        raise AssertionError("非法 format 应被 422 拒绝")
    except urllib.error.HTTPError as e:
        assert e.code == 422, f"非法 format 应 422, 实际 {e.code}"
        print(f"[preview pdf] status=422 (rejected as expected)")

    print("\n✅ 所有 P2 冒烟断言通过")


if __name__ == "__main__":
    asyncio.run(main())
