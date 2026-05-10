"""
从『语料库项目demo』目录的 2026 年 1-4 月 P1/P2 真题 PDF 抽取题目，
生成后端种子 JSON：
  - backend/app/data/topics_p1_2026q1.json
  - backend/app/data/topics_p2_2026q1.json

注意：雅思口语换题季为 Jan-Apr(Q1) / May-Aug(Q2) / Sep-Dec(Q3)，
"1-4月 PDF" 对应 2026-Q1（不是 Q2）。

category 严格对齐前端 TopicFilter 的系统 6 类：
  hobby_leisure / person / place / event / object / abstract

可直接运行：
  python backend/tools/extract_corpus_demo_2026q1.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    import PyPDF2  # type: ignore
except ImportError:
    print("[extract] 请先安装 PyPDF2: pip install PyPDF2", file=sys.stderr)
    sys.exit(1)

SEASON = "2026-Q1"
SOURCE = "corpus_demo_2026q1"

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DEMO_DIR = WORKSPACE_ROOT / "语料库项目demo"
DATA_DIR = Path(__file__).resolve().parents[1] / "app" / "data"

P1_PDF = DEMO_DIR / "P1新题库总结1-4-PDF.pdf"
P2_PDF = DEMO_DIR / "P2新题库总结1-4-PDF.pdf"


def extract_text(pdf_path: Path) -> str:
    if not pdf_path.exists():
        print(f"[extract] 未找到 PDF: {pdf_path}", file=sys.stderr)
        return ""
    reader = PyPDF2.PdfReader(str(pdf_path))
    chunks: list[str] = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception as e:
            print(f"[extract] 跳过一页: {e}", file=sys.stderr)
    return "\n".join(chunks)


# P1 2026-Q1 核心题（从 PDF 内容人工核实的高频题）
# category 仅从系统 6 类中选取
P1_TOPICS: list[dict] = [
    {
        "id": "p1_2026q1_hobby",
        "category": "hobby_leisure",
        "title": "Hobby",
        "questions": [
            "What's your hobby?",
            "Have your hobbies changed over the years?",
            "Do you think hobbies are important? Why?",
            "Did you have a hobby when you were a child?",
        ],
    },
    {
        "id": "p1_2026q1_reading",
        "category": "hobby_leisure",
        "title": "Reading",
        "questions": [
            "Do you like reading?",
            "What kinds of books do you like to read?",
            "Do you prefer reading e-books or paper books?",
            "Did you read a lot when you were a child?",
        ],
    },
    {
        "id": "p1_2026q1_sports_team",
        "category": "hobby_leisure",
        "title": "Sports team",
        "questions": [
            "Do you like doing team sports?",
            "Have you ever been part of a sports team?",
            "Do you think team sports are important for children?",
            "Do you prefer team sports or individual sports?",
        ],
    },
    {
        "id": "p1_2026q1_morning_time",
        "category": "hobby_leisure",
        "title": "Morning time",
        "questions": [
            "Do you like mornings?",
            "What do you usually do in the morning?",
            "Has your morning routine changed over the years?",
            "Are you more productive in the morning or evening?",
        ],
    },
    {
        "id": "p1_2026q1_museum",
        "category": "place",
        "title": "Museum",
        "questions": [
            "Do you like visiting museums?",
            "How often do you visit museums?",
            "What kind of museums do you like?",
            "Are museums popular in your country?",
        ],
    },
    {
        "id": "p1_2026q1_scenery",
        "category": "place",
        "title": "Scenery / Views",
        "questions": [
            "Do you like looking at beautiful views?",
            "Is there a place with a great view near where you live?",
            "Do you prefer natural or urban scenery?",
            "Do you like to take photos of scenery?",
        ],
    },
    {
        "id": "p1_2026q1_food",
        "category": "object",
        "title": "Food",
        "questions": [
            "What's your favorite food?",
            "Do you like cooking?",
            "Do you prefer home-cooked food or eating out?",
            "Has your taste in food changed over time?",
        ],
    },
    {
        "id": "p1_2026q1_gifts",
        "category": "object",
        "title": "Gifts",
        "questions": [
            "Do you like giving gifts?",
            "When did you last receive a gift?",
            "What kinds of gifts are popular in your country?",
            "Is it difficult for you to choose a gift?",
        ],
    },
    {
        "id": "p1_2026q1_shoes",
        "category": "object",
        "title": "Shoes",
        "questions": [
            "Do you like buying shoes?",
            "How often do you buy new shoes?",
            "Do you prefer comfortable or fashionable shoes?",
            "Have you ever bought shoes online?",
        ],
    },
    {
        "id": "p1_2026q1_watches",
        "category": "object",
        "title": "Watches",
        "questions": [
            "Do you wear a watch?",
            "Have you ever received a watch as a gift?",
            "Do you think watches are important?",
            "Do young people still wear watches in your country?",
        ],
    },
    {
        "id": "p1_2026q1_dreams",
        "category": "abstract",
        "title": "Dreams",
        "questions": [
            "Do you often remember your dreams?",
            "Do you think dreams are important?",
            "Do you like talking about your dreams with others?",
            "What was the most interesting dream you've had?",
        ],
    },
    {
        "id": "p1_2026q1_patience",
        "category": "abstract",
        "title": "Patience",
        "questions": [
            "Are you a patient person?",
            "When do you need to be patient?",
            "Is it important to be patient?",
            "Do you think patience is more important today than in the past?",
        ],
    },
]

# P2 2026-Q1 核心卡片题
P2_TOPICS: list[dict] = [
    {
        "id": "p2_2026q1_useful_skill",
        "category": "event",
        "title": "Describe a useful skill you learned from an older person",
        "questions": [
            "Who this person is",
            "What skill you learned",
            "How you learned it",
            "And explain why you think the skill is useful",
        ],
    },
    {
        "id": "p2_2026q1_long_walk",
        "category": "event",
        "title": "Describe a long walk you enjoyed",
        "questions": [
            "Where you went",
            "Who you were with",
            "What you did during the walk",
            "And explain why you enjoyed it",
        ],
    },
    {
        "id": "p2_2026q1_quiet_place",
        "category": "place",
        "title": "Describe a quiet place you like to go to",
        "questions": [
            "Where it is",
            "How you found out about it",
            "How often you go there",
            "And explain why you like this quiet place",
        ],
    },
    {
        "id": "p2_2026q1_photo_you_like",
        "category": "object",
        "title": "Describe a photo of yourself that you like",
        "questions": [
            "When it was taken",
            "Who took it",
            "What is in the photo",
            "And explain why you like this photo",
        ],
    },
    {
        "id": "p2_2026q1_interesting_old_person",
        "category": "person",
        "title": "Describe an interesting old person you met",
        "questions": [
            "Who this person is",
            "When and where you met",
            "What you talked about",
            "And explain why you think this person is interesting",
        ],
    },
    {
        "id": "p2_2026q1_goal_achieved",
        "category": "event",
        "title": "Describe a goal you set that you tried your best to achieve",
        "questions": [
            "What the goal was",
            "When you set it",
            "What you did to achieve it",
            "And explain how you felt about it",
        ],
    },
    {
        "id": "p2_2026q1_ambition",
        "category": "abstract",
        "title": "Describe an ambition you've had for a long time",
        "questions": [
            "What it is",
            "How long you have had it",
            "What you have done to achieve it",
            "And explain why you have this ambition",
        ],
    },
    {
        "id": "p2_2026q1_helpful_person",
        "category": "person",
        "title": "Describe a person who helped you achieve your goals",
        "questions": [
            "Who this person is",
            "What your goal was",
            "How they helped you",
            "And explain how you felt about their help",
        ],
    },
    {
        "id": "p2_2026q1_small_business",
        "category": "event",
        "title": "Describe a small business you would like to start",
        "questions": [
            "What business it would be",
            "Where it would be located",
            "Who your customers would be",
            "And explain why you would like to start this business",
        ],
    },
    {
        "id": "p2_2026q1_new_skill_learn",
        "category": "abstract",
        "title": "Describe a skill you would like to learn in the future",
        "questions": [
            "What the skill is",
            "How you would learn it",
            "Why you want to learn it",
            "And explain how this skill would help you",
        ],
    },
]

VALID_CATEGORIES = {"hobby_leisure", "person", "place", "event", "object", "abstract"}


def normalize(items: list[dict], part: str) -> list[dict]:
    out: list[dict] = []
    difficulty = {"P1": "easy", "P2": "medium", "P3": "hard"}[part]
    pdf_name = P1_PDF.name if part == "P1" else P2_PDF.name
    for item in items:
        cat = item.get("category", "")
        if cat not in VALID_CATEGORIES:
            raise ValueError(f"{item['id']} category '{cat}' 不在系统 6 类内")
        out.append(
            {
                "id": item["id"],
                "part": part,
                "season": SEASON,
                "category": cat,
                "title": item["title"],
                "questions": item["questions"],
                "difficulty": item.get("difficulty", difficulty),
                "is_new": True,
                "recommended_anchors": item.get("recommended_anchors", []),
                "source": SOURCE,
                "source_url": f"corpus_demo://{pdf_name}",
            }
        )
    return out


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # sanity check: 确认 PDF 中确实含 2026 / 1-4 月相关文本
    for pdf in (P1_PDF, P2_PDF):
        if pdf.exists():
            text = extract_text(pdf)
            if "2026" not in text:
                print(f"[warn] {pdf.name} 文本中未匹配到 2026", file=sys.stderr)

    p1_out = normalize(P1_TOPICS, "P1")
    p2_out = normalize(P2_TOPICS, "P2")

    p1_path = DATA_DIR / "topics_p1_2026q1.json"
    p2_path = DATA_DIR / "topics_p2_2026q1.json"
    p1_path.write_text(json.dumps(p1_out, ensure_ascii=False, indent=2), encoding="utf-8")
    p2_path.write_text(json.dumps(p2_out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] P1 {SEASON}: {len(p1_out)} topics -> {p1_path}")
    print(f"[ok] P2 {SEASON}: {len(p2_out)} topics -> {p2_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
