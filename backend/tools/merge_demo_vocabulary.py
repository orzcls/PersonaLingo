"""
从『语料库项目demo』的两个 docx 抽取地道词汇/短语，增量合并到
  backend/app/data/idiomatic_vocabulary.json

解析策略（兼容 5/6 列左右对照表格）：
1. 每个 table 第一行若所有 cell 文本相同且含中英文 → 作为 category 名称
2. 遍历剩余行，依据列数提取左右两对 (中文意义, 英文表达)：
   - 6 列: (row[1], row[2]) 与 (row[4], row[5])
   - 5 列: (row[0], row[1]) 与 (row[3], row[4])
   - 4 列: (row[0], row[1]) 与 (row[2], row[3])
   - 3 列: (row[0], row[1]) 单对
   - 2 列: (row[0], row[1]) 单对（可能是 like/dislike 对照，此时 cell 本身即英文）
3. 若候选英文含 '/' → 拆成多条词条
4. 按 word 小写去重 合并入现有 JSON

运行：
  python backend/tools/merge_demo_vocabulary.py
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document  # python-docx
except ImportError:
    print("[merge] pip install python-docx", file=sys.stderr)
    sys.exit(1)

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DEMO_DIR = WORKSPACE_ROOT / "语料库项目demo"
VOCAB_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "idiomatic_vocabulary.json"

SOURCES = [
    (DEMO_DIR / "PPChu冲鸭小分队—地道单词.docx", "PPChu冲鸭小分队—地道单词"),
    (DEMO_DIR / "程同学 课堂精练.docx", "程同学 课堂精练"),
]

HAS_EN = re.compile(r"[A-Za-z]{3,}")
HAS_ZH = re.compile(r"[\u4e00-\u9fff]")
SKIP_TOKENS = {"形容词", "名词或者词组", "动词", "词性", "短语", "副词", "", "关于"}


def is_english(s: str) -> bool:
    return bool(HAS_EN.search(s))


def is_chinese(s: str) -> bool:
    return bool(HAS_ZH.search(s))


def norm(s: str) -> str:
    return (s or "").strip().replace("\u3000", " ")


def split_english(en: str) -> list[str]:
    """英文表达里可能含 '/'、'，' 分隔多个同义词，拆分"""
    if not en:
        return []
    # 优先按 '/' 拆
    parts = re.split(r"[\/、，]", en)
    parts = [p.strip() for p in parts if p.strip()]
    # 剔除过长者（大概是例句，不拆，整体保留）
    return parts if parts else [en.strip()]


def extract_pairs_from_row(cells: list[str]) -> list[tuple[str, str]]:
    """返回 [(chinese_meaning, english_expression), ...]"""
    cells = [norm(c) for c in cells]
    pairs: list[tuple[str, str]] = []
    n = len(cells)

    def try_pair(zh: str, en: str):
        if not zh or not en:
            return
        if zh in SKIP_TOKENS:
            return
        if not is_chinese(zh):
            return
        if not is_english(en):
            return
        pairs.append((zh, en))

    if n >= 6:
        # 词性 | 中A | 英A | 空 | 中B | 英B
        try_pair(cells[1], cells[2])
        try_pair(cells[4], cells[5])
    elif n == 5:
        # 中A | 英A | 空 | 中B | 英B
        try_pair(cells[0], cells[1])
        try_pair(cells[3], cells[4])
    elif n == 4:
        # 中A | 英A | 中B | 英B
        try_pair(cells[0], cells[1])
        try_pair(cells[2], cells[3])
    elif n == 3:
        try_pair(cells[0], cells[1])
    elif n == 2:
        # 可能是 left/right 英文对照（like / dislike）—— 直接当英文收集
        for c in cells:
            if is_english(c) and not is_chinese(c):
                pairs.append(("", c))
    return pairs


def category_name(tbl) -> str:
    first = tbl.rows[0]
    texts = [norm(c.text) for c in first.cells]
    uniq = {t for t in texts if t}
    if len(uniq) == 1:
        name = next(iter(uniq))
        if is_english(name) or is_chinese(name):
            return name
    return ""


def parse_docx(path: Path, src_label: str) -> list[dict]:
    """返回 [{category, chinese, english, source}] 原始条目列表"""
    out: list[dict] = []
    if not path.exists():
        print(f"[merge] missing: {path}", file=sys.stderr)
        return out
    doc = Document(str(path))
    for ti, tbl in enumerate(doc.tables):
        cat = category_name(tbl) or f"{src_label} · 杂项 {ti}"
        body = tbl.rows[1:] if category_name(tbl) else tbl.rows
        for row in body:
            cells = [c.text for c in row.cells]
            for zh, en in extract_pairs_from_row(cells):
                out.append({
                    "category": cat,
                    "chinese": zh,
                    "english": en,
                    "source": src_label,
                })
    return out


def to_word_entry(zh: str, en: str, cat: str) -> dict:
    """把原始 (中文, 英文) 规整成 idiomatic_vocabulary.json 里的 word 条目格式"""
    # 英文可能含多个同义词（'/' 分隔） —— 取最短者作为 word，整体作为 meaning/example
    parts = split_english(en)
    word = min(parts, key=len) if parts else en
    # band_level 估算：短词 6.0+，含括号/短语 6.5+，较长 7.0+
    if len(word.split()) >= 3:
        band = "7.0+"
    elif len(word) <= 6:
        band = "6.0+"
    else:
        band = "6.5+"
    return {
        "word": word.strip(),
        "meaning": zh,
        "example": "",
        "band_level": band,
        "usage_topics": [cat.split(" ")[0]] if cat else [],
    }


def main() -> int:
    if not VOCAB_PATH.exists():
        print(f"[merge] 未找到 {VOCAB_PATH}", file=sys.stderr)
        return 1
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    categories: list[dict] = vocab.get("categories", [])
    # 建立 word -> (cat_idx, word_idx) 索引（小写去重）
    existing: dict[str, tuple[int, int]] = {}
    for ci, cat in enumerate(categories):
        for wi, w in enumerate(cat.get("words", [])):
            existing[w["word"].lower()] = (ci, wi)

    cat_index: dict[str, int] = {cat["category"]: i for i, cat in enumerate(categories)}

    added = 0
    skipped = 0
    for path, label in SOURCES:
        raw = parse_docx(path, label)
        for item in raw:
            entry = to_word_entry(item["chinese"], item["english"], item["category"])
            key = entry["word"].lower()
            if not key or key in existing:
                skipped += 1
                continue
            # 找/建 category（加 demo 来源后缀，避免与老分类混淆）
            cat_name = f"{item['category']} (demo)"
            if cat_name not in cat_index:
                categories.append({"category": cat_name, "words": []})
                cat_index[cat_name] = len(categories) - 1
            ci = cat_index[cat_name]
            categories[ci]["words"].append(entry)
            existing[key] = (ci, len(categories[ci]["words"]) - 1)
            added += 1

    vocab["categories"] = categories
    # 更新 source 字段为多来源
    vocab["source"] = "PPChu冲鸭小分队—地道单词 + 程同学 课堂精练"
    vocab["version"] = "1.1"

    # 备份
    backup = VOCAB_PATH.with_suffix(".json.bak")
    if not backup.exists():
        backup.write_text(json.dumps(json.load(open(VOCAB_PATH, "r", encoding="utf-8")),
                                     ensure_ascii=False, indent=2), encoding="utf-8")

    VOCAB_PATH.write_text(
        json.dumps(vocab, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total_words = sum(len(c.get("words", [])) for c in categories)
    print(f"[ok] added {added} new words, skipped {skipped} duplicates.")
    print(f"[ok] total categories: {len(categories)}, total words: {total_words}")
    print(f"[ok] written -> {VOCAB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
