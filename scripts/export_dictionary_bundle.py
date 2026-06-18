#!/usr/bin/env python3
"""Экспорт единого словаря: слово, определение, пример, картинка."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_profanity_review import word_entries  # noqa: E402
from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402
from profanity_curated_data import CURATED_PROFANITY_NOUNS  # noqa: E402
from word_review_enrichment import load_enrichment  # noqa: E402

OUT_JSON = ROOT / "sources" / "dictionary-bundle.json"
OUT_MD = ROOT / "sources" / "dictionary-bundle.md"


def export_bundle() -> dict:
    enrichment = load_enrichment()
    entries = word_entries(enrichment)

    words = []
    for e in entries:
        words.append(
            {
                "word": e["word"],
                "length": e["len"],
                "sources": e["sources"],
                "definition": e["definition"],
                "example": e.get("example"),
                "example_source": e.get("example_source"),
                "example_title": e.get("example_title"),
                "image": e.get("image"),
                "image_source": e.get("image_source"),
            }
        )

    mat_only = sorted(w for w in CURATED_PROFANITY_NOUNS if w not in CURATED_DVACH_NOUNS)
    dvach_only = sorted(w for w in CURATED_DVACH_NOUNS if w not in CURATED_PROFANITY_NOUNS)
    both = sorted(CURATED_PROFANITY_NOUNS & CURATED_DVACH_NOUNS)

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_words": len(words),
            "mat_words": len(CURATED_PROFANITY_NOUNS),
            "dvach_words": len(CURATED_DVACH_NOUNS),
            "overlap": len(both),
            "with_example": sum(1 for w in words if w.get("example")),
            "with_image": sum(1 for w in words if w.get("image")),
        },
        "word_lists": {
            "mat_only": mat_only,
            "dvach_only": dvach_only,
            "both": both,
        },
        "words": words,
    }


def write_markdown(bundle: dict) -> None:
    lines = [
        "# Словарь Хуердли — полный бандл",
        "",
        f"Сгенерировано: {bundle['generated_at']}",
        f"Всего слов: {bundle['stats']['total_words']}, "
        f"с примером: {bundle['stats']['with_example']}, "
        f"с картинкой: {bundle['stats']['with_image']}",
        "",
    ]
    for item in bundle["words"]:
        src = ", ".join(item["sources"])
        lines.append(f"## {item['word']} ({item['length']}, {src})")
        lines.append("")
        lines.append(item["definition"] or "—")
        lines.append("")
        if item.get("example"):
            lines.append(f"> {item['example']}")
            if item.get("example_source"):
                lines.append(f"> — [{item.get('example_title') or 'источник'}]({item['example_source']})")
            lines.append("")
        if item.get("image"):
            lines.append(f"![{item['word']}]({item['image']})")
            if item.get("image_source"):
                lines.append(f"Картинка: {item['image_source']}")
            lines.append("")
        lines.append("---")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    bundle = export_bundle()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(bundle)
    print(f"→ {OUT_JSON}")
    print(f"→ {OUT_MD}")
    print(
        f"  {bundle['stats']['total_words']} слов, "
        f"примеров {bundle['stats']['with_example']}, "
        f"картинок {bundle['stats']['with_image']}"
    )


if __name__ == "__main__":
    main()
