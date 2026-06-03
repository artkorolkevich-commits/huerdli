#!/usr/bin/env python3
"""
Сборка словарей для «Хуердли».

Обычные существительные: Harrix/Russian-Nouns
Мат: проверенный curated-список (scripts/profanity_curated_data.py)
"""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

try:
    import pymorphy2  # noqa: F401 — для будущего авто-расширения
except ImportError:
    print("Установите зависимости: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from profanity_curated_data import CURATED_PROFANITY_NOUNS, MIN_PROFANITY_WORDS  # noqa: E402

SOURCES_DIR = ROOT / "sources"
OUT_DIR = ROOT / "dictionaries"

NOUNS_URL = "https://raw.githubusercontent.com/Harrix/Russian-Nouns/v2.0/dist/russian_nouns.txt"


def norm(word: str) -> str:
    word = word.strip().lower().replace("ё", "е")
    return re.sub(r"[^а-я]", "", word)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    print(f"  загрузка {url}")
    try:
        data = urllib.request.urlopen(url, timeout=60).read()
    except urllib.error.URLError as exc:
        raise SystemExit(f"Не удалось скачать {url}: {exc}") from exc
    dest.write_bytes(data)


def load_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def build_normal_nouns(nouns_path: Path) -> dict[int, list[str]]:
    words: set[str] = set()
    for line in load_lines(nouns_path):
        w = norm(line)
        if not w or not re.fullmatch(r"[а-я]+", w):
            continue
        if 5 <= len(w) <= 7:
            words.add(w)

    by_len: dict[int, list[str]] = defaultdict(list)
    for w in sorted(words):
        by_len[len(w)].append(w.upper())
    return by_len


def build_profanity_nouns() -> dict[int, list[str]]:
    by_len: dict[int, list[str]] = defaultdict(list)
    for w in sorted(CURATED_PROFANITY_NOUNS):
        normalized = norm(w)
        if not normalized or not re.fullmatch(r"[а-я]+", normalized):
            raise SystemExit(f"Матовое слово не на кириллице: {w!r}")
        if len(normalized) not in (5, 6):
            raise SystemExit(f"Матовое слово не 5–6 букв: {w!r} ({len(normalized)})")
        by_len[len(normalized)].append(normalized.upper())

    total_56 = len(by_len[5]) + len(by_len[6])
    if total_56 < MIN_PROFANITY_WORDS:
        raise SystemExit(
            f"Матовых слов (5–6 букв) только {total_56}, нужно минимум {MIN_PROFANITY_WORDS}. "
            "Добавьте 5-буквенные слова в scripts/profanity_curated_data.py"
        )

    return by_len


def write_dict(path: Path, words: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(words) + ("\n" if words else ""), encoding="utf-8")


def main() -> None:
    print("Сборка словарей «Хуердли»…")
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    nouns_file = SOURCES_DIR / "russian_nouns.txt"
    download(NOUNS_URL, nouns_file)

    print("\nОбычные существительные (Harrix/Russian-Nouns):")
    normal = build_normal_nouns(nouns_file)
    for length in (5, 6, 7):
        out = OUT_DIR / f"ru-nouns-{length}.txt"
        write_dict(out, normal[length])
        print(f"  {length} букв: {len(normal[length])} → {out.name}")

    print("\nМат (curated, только кириллица, 5–6 букв для игры):")
    profanity = build_profanity_nouns()
    for length in (5, 6):
        out = OUT_DIR / f"ru-profanity-nouns-{length}.txt"
        write_dict(out, profanity[length])
        print(f"  {length} букв: {len(profanity[length])} → {out.name}")

    total = len(profanity[5]) + len(profanity[6])
    print(f"\nИтого матовых слов (5+6): {total} (минимум {MIN_PROFANITY_WORDS})")
    print("Готово.")


if __name__ == "__main__":
    main()
