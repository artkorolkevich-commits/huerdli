#!/usr/bin/env python3
"""
Сборка словарей для «Хуердли».

Обычные существительные: Harrix/Russian-Nouns + фильтр word_rules.py
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
    import pymorphy2
except ImportError:
    print("Установите зависимости: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from profanity_curated_data import CURATED_PROFANITY_NOUNS, MIN_PROFANITY_WORDS  # noqa: E402
from dvach_curated_data import CURATED_DVACH_NOUNS, MIN_DVACH_WORDS  # noqa: E402
from guess_supplement_data import GUESS_SUPPLEMENT  # noqa: E402
from word_rules import (  # noqa: E402
    passes_normal_dictionary_rules,
    passes_profanity_rules,
    passes_dvach_rules,
    passes_guess_extended_rules,
    reject_reason_normal,
    reject_reason_profanity,
    reject_reason_dvach,
)

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


def build_normal_nouns(nouns_path: Path, morph: pymorphy2.MorphAnalyzer) -> dict[int, list[str]]:
    words: set[str] = set()
    rejected: list[tuple[str, str]] = []

    for line in load_lines(nouns_path):
        w = norm(line)
        if not w or not re.fullmatch(r"[а-я]+", w):
            continue
        if not (5 <= len(w) <= 6):
            continue
        if passes_normal_dictionary_rules(morph, w):
            words.add(w)
        else:
            reason = reject_reason_normal(morph, w)
            if reason:
                rejected.append((w, reason))

    by_len: dict[int, list[str]] = defaultdict(list)
    for w in sorted(words):
        by_len[len(w)].append(w.upper())

    if rejected:
        print(f"  отфильтровано: {len(rejected)} (примеры: {', '.join(w for w, _ in rejected[:8])})")
    return by_len


def build_guess_extended(nouns_path: Path, dvach_words: set[str]) -> dict[int, list[str]]:
    """7–8 букв: только для ввода, максимальный охват Harrix + двач + дополнения."""
    words: set[str] = set()

    for line in load_lines(nouns_path):
        w = norm(line)
        if passes_guess_extended_rules(w):
            words.add(w)

    for w in dvach_words:
        normalized = norm(w)
        if passes_guess_extended_rules(normalized):
            words.add(normalized)

    for length, supplement in GUESS_SUPPLEMENT.items():
        for w in supplement:
            normalized = norm(w)
            if len(normalized) == length and passes_guess_extended_rules(normalized):
                words.add(normalized)

    by_len: dict[int, list[str]] = defaultdict(list)
    for w in sorted(words):
        by_len[len(w)].append(w.upper())
    return by_len


def build_profanity_nouns() -> dict[int, list[str]]:
    by_len: dict[int, list[str]] = defaultdict(list)
    for w in sorted(CURATED_PROFANITY_NOUNS):
        normalized = norm(w)
        if not passes_profanity_rules(w):
            reason = reject_reason_profanity(w) or "не проходит правила"
            raise SystemExit(f"Матовое слово отклонено ({reason}): {w!r}")
        by_len[len(normalized)].append(normalized.upper())

    total_56 = len(by_len[5]) + len(by_len[6])
    if total_56 < MIN_PROFANITY_WORDS:
        raise SystemExit(
            f"Матовых слов (5–6 букв) только {total_56}, нужно минимум {MIN_PROFANITY_WORDS}. "
            "Добавьте 5-буквенные слова в scripts/profanity_curated_data.py"
        )

    return by_len


def build_dvach_nouns() -> dict[int, list[str]]:
    by_len: dict[int, list[str]] = defaultdict(list)
    for w in sorted(CURATED_DVACH_NOUNS):
        normalized = norm(w)
        if not passes_dvach_rules(w):
            reason = reject_reason_dvach(w) or "не проходит правила"
            raise SystemExit(f"Двач-слово отклонено ({reason}): {w!r}")
        by_len[len(normalized)].append(normalized.upper())

    total = sum(len(by_len.get(n, [])) for n in (5, 6, 7, 8))
    if total < MIN_DVACH_WORDS:
        raise SystemExit(
            f"Слов двача только {total}, нужно минимум {MIN_DVACH_WORDS}. "
            "Запустите: python scripts/collect_dvach_words.py"
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

    morph = pymorphy2.MorphAnalyzer()

    print("\nОбычные существительные (Harrix, 5–6 букв — загадываются в классический день):")
    normal = build_normal_nouns(nouns_file, morph)
    for length in (5, 6):
        out = OUT_DIR / f"ru-nouns-{length}.txt"
        write_dict(out, normal[length])
        print(f"  {length} букв: {len(normal[length])} → {out.name}")

    print("\nДвач / рунет (curated, 5–8 букв):")
    dvach = build_dvach_nouns()
    for length in (5, 6, 7, 8):
        out = OUT_DIR / f"ru-dvach-nouns-{length}.txt"
        write_dict(out, dvach.get(length, []))
        print(f"  {length} букв: {len(dvach.get(length, []))} → {out.name}")

    total_d = sum(len(dvach.get(n, [])) for n in (5, 6, 7, 8))
    print(f"\nИтого слов двача (5–8): {total_d} (минимум {MIN_DVACH_WORDS})")

    dvach_all = {norm(w) for w in CURATED_DVACH_NOUNS}

    print("\nРасширенный ввод (7–8 букв, только для проверки букв, не загадывается):")
    guess_ext = build_guess_extended(nouns_file, dvach_all)
    for length in (7, 8):
        out = OUT_DIR / f"ru-guess-{length}.txt"
        write_dict(out, guess_ext.get(length, []))
        print(f"  {length} букв: {len(guess_ext.get(length, []))} → {out.name}")

    print("\nМат (curated, только кириллица, 5–6 букв для ввода):")
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
