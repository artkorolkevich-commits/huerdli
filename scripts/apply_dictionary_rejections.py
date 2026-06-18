#!/usr/bin/env python3
"""Применить dictionary-rejected.json к curated-спискам."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from profanity_curated_data import CURATED_PROFANITY_NOUNS  # noqa: E402
from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402

COLLECT_PATH = SCRIPTS / "collect_dvach_words.py"
PROFANITY_PATH = SCRIPTS / "profanity_curated_data.py"
REJECTED_LOG = ROOT / "sources" / "dictionary-rejected-applied.json"


def load_rejections(path: Path) -> tuple[set[str], set[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    mat: set[str] = set()
    dvach: set[str] = set()
    for item in data["rejected"]:
        w = item["word"].strip().lower().replace("ё", "е")
        for src in item["sources"]:
            if src == "mat":
                mat.add(w)
            elif src == "dvach":
                dvach.add(w)
    return mat, dvach


def write_profanity(words: set[str]) -> None:
    body = ",\n".join(f"    {w!r}" for w in sorted(words))
    text = PROFANITY_PATH.read_text(encoding="utf-8")
    new_block = f"CURATED_PROFANITY_NOUNS: frozenset[str] = frozenset({{\n{body},\n}})"
    text = re.sub(
        r"CURATED_PROFANITY_NOUNS: frozenset\[str\] = frozenset\(\{.*?\}\)",
        new_block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    PROFANITY_PATH.write_text(text, encoding="utf-8")


def update_user_rejected(dvach_reject: set[str]) -> None:
    text = COLLECT_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"USER_REJECTED: frozenset\[str\] = frozenset\(\{([^}]*)\}\)",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise SystemExit("USER_REJECTED не найден в collect_dvach_words.py")
    current = {
        w.strip().strip('"').strip("'")
        for w in match.group(1).replace("\n", " ").split(",")
        if w.strip().strip('"').strip("'")
    }
    merged = sorted(current | dvach_reject)
    body = ",\n".join(f'    "{w}"' for w in merged)
    new_block = f"USER_REJECTED: frozenset[str] = frozenset({{\n{body},\n}})"
    text = re.sub(
        r"USER_REJECTED: frozenset\[str\] = frozenset\(\{.*?\}\)",
        new_block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    COLLECT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    reject_path = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "dictionary-rejected.json")
    if not reject_path.exists():
        reject_path = Path("/Users/artkorol/Downloads/dictionary-rejected.json")
    if not reject_path.exists():
        raise SystemExit(f"Файл не найден: {reject_path}")

    mat_reject, dvach_reject = load_rejections(reject_path)

    new_mat = CURATED_PROFANITY_NOUNS - mat_reject
    new_dvach_preview = CURATED_DVACH_NOUNS - dvach_reject

    removed_mat = sorted(CURATED_PROFANITY_NOUNS & mat_reject)
    removed_dvach = sorted(CURATED_DVACH_NOUNS & dvach_reject)

    write_profanity(new_mat)
    update_user_rejected(dvach_reject)

    REJECTED_LOG.write_text(
        json.dumps(
            {
                "source_file": str(reject_path),
                "removed_mat": removed_mat,
                "removed_dvach": removed_dvach,
                "mat_remaining": len(new_mat),
                "dvach_remaining_preview": len(new_dvach_preview),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Мат: убрано {len(removed_mat)}, останется {len(new_mat)}")
    print(f"Двач: убрано {len(removed_dvach)}, в USER_REJECTED +{len(dvach_reject - set())}")
    print(f"→ {REJECTED_LOG}")


if __name__ == "__main__":
    main()
