#!/usr/bin/env python3
"""Аудит картинок на дашборде ревью: кто без иллюстрации и почему."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402
from meme_review_overrides import MEME_NEOLURK_TITLE_MAP, MEME_REVIEW_OVERRIDES  # noqa: E402
from word_review_enrichment import CACHE_PATH, load_enrichment  # noqa: E402

# Слова, где картинка мема обычно не нужна (лексика, техника, мат в дваче).
SKIP_IMAGE_CATEGORIES = {
    "tech": {
        "авито", "бекап", "бустер", "взлом", "вирус", "доксер", "крекер", "малвар",
        "руткит", "сватер", "троян", "фишинг", "читкод", "ботнет",
    },
    "generic_slang": {
        "базар", "бампер", "банхам", "баффер", "башорг", "билдер", "бордач",
        "вайбик", "вангую", "геймленд", "геймпасс", "геймплей", "гифка", "гринд",
        "гриндер", "деген", "демка", "дискач", "додик", "канон", "коллаб", "крафт",
        "крафтер", "кроспост", "кунгфу", "ламер", "лампа", "лейбл", "лонгрид",
        "лутер", "макак", "модель", "набег", "паблик", "паста", "подкаст", "попан",
        "пруфики", "рашка", "рейдж", "скетч", "скилл", "скиллз", "спидран",
        "тайпан", "телега", "тредик", "триггер", "фармер", "форсер", "форсинг",
        "хайлайт", "хайпер", "хостер", "чандра", "чендж", "шиппер", "ютубер",
    },
    "profanity_in_dvach": {
        "блядка", "блядь", "гнида", "говнюк", "дурак", "задик", "козел", "кретин",
        "мразь", "мудло", "нахуй", "падла", "пездюк", "пиздеж", "пидорг", "пидрил",
        "похер", "стерва", "тварь", "фаггот", "фагот", "хуйло", "хуймэн", "чушпан",
    },
    "chan_suffix_noise": {
        "альфачан", "галустян", "метачан", "модтян", "сбертян", "тэгосрач",
        "трипфаг", "тяньши", "тянка",
    },
}

SKIP_ALL = set().union(*SKIP_IMAGE_CATEGORIES.values())


def main() -> None:
    enrichment = load_enrichment()
    with_img: list[str] = []
    no_img_meme: list[str] = []
    no_img_skip: list[str] = []
    no_img_other: list[str] = []

    for w in sorted(CURATED_DVACH_NOUNS):
        if enrichment.get(w, {}).get("image"):
            with_img.append(w)
            continue
        if w in SKIP_ALL:
            no_img_skip.append(w)
        elif w in MEME_NEOLURK_TITLE_MAP or w in MEME_REVIEW_OVERRIDES:
            no_img_meme.append(w)
        else:
            no_img_other.append(w)

    report = {
        "total_dvach": len(CURATED_DVACH_NOUNS),
        "with_image": len(with_img),
        "without_image": len(CURATED_DVACH_NOUNS) - len(with_img),
        "meme_candidates_still_missing": no_img_meme,
        "low_priority_no_image": no_img_skip,
        "other_without_image": no_img_other,
    }
    out = SCRIPTS.parent / "sources" / "meme-images-audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Двач: {report['total_dvach']}, с картинкой: {report['with_image']}, без: {report['without_image']}")
    print(f"  мемы без картинки (приоритет): {len(no_img_meme)}")
    print(f"  лексика/мат — картинка не нужна: {len(no_img_skip)}")
    print(f"  прочие без картинки: {len(no_img_other)}")
    print(f"→ {out}")


if __name__ == "__main__":
    main()
