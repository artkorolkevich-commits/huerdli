#!/usr/bin/env python3
"""Подобрать картинки для всех двач-слов без иллюстрации."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402
from meme_review_overrides import MEME_NEOLURK_TITLE_MAP, MEME_REVIEW_OVERRIDES  # noqa: E402
from word_review_enrichment import (  # noqa: E402
    CACHE_PATH,
    api,
    fetch_article,
    first_sentence,
    guess_titles,
    load_enrichment,
    load_title_index,
    normalize,
)

# Заголовки, дающие ложные картинки — отклоняем.
BAD_IMAGE_TITLES = {
    "мелкий жемчуг",
    "банановая кожура",
    "about memes",
}

BAD_IMAGE_URL_PARTS = (
    "old_man_sym.png",
    "about_memes.jpg",
    "magnify-clip.png",
)


def titles_close(a: str, b: str) -> bool:
    a, b = normalize(a), normalize(b)
    if a == b or a in b or b in a:
        return True
    if len(a) >= 4 and len(b) >= 4 and abs(len(a) - len(b)) <= 1:
        # одна вставка/замена (булшит ↔ буллшит)
        if len(a) == len(b):
            return sum(x != y for x, y in zip(a, b)) <= 1
        short, long = (a, b) if len(a) < len(b) else (b, a)
        for i in range(len(long)):
            if long[:i] + long[i + 1 :] == short:
                return True
    return False


# Заголовки-приманки для сленга без своей статьи.
EXTRA_SEARCH: dict[str, list[str]] = {
    "альфачан": ["Альфач"],
    "баянист": ["Баян"],
    "бибизян": ["Бибизяна", "Мем"],
    "богач": ["Богач"],
    "булшит": ["Буллшит"],
    "вейпер": ["Вейп"],
    "говновоз": ["Говно"],
    "говнофон": ["Говно"],
    "говнохуй": ["Говно"],
    "кавай": ["Кавай"],
    "кочан": ["Кочан"],
    "лолчто": ["Лол"],
    "мемодел": ["Мем"],
    "метовик": ["Мета"],
    "нацик": ["Нацик"],
    "нейман": ["Нейман"],
    "неймфаг": ["Неймфаг"],
    "нейроарт": ["Нейроарт"],
    "нетфаг": ["Нетфаг", "Фаг"],
    "ниточка": ["Нитка"],
    "огонек": ["Огонёк"],
    "озвучка": ["Озвучка"],
    "пепекун": ["Пепе", "Pepe"],
    "пепефаг": ["Пепе", "Pepe"],
    "пепечан": ["Пепе", "Pepe"],
    "пикча": ["Пикча"],
    "пистифаг": ["Пистолет"],
    "постер": ["Постер"],
    "прадит": ["Reddit"],
    "реактор": ["Реактор"],
    "реакция": ["Реакция"],
    "резун": ["Резня"],
    "рейпост": ["Репост"],
    "рофлик": ["Рофл"],
    "рофлян": ["Рофл"],
    "ручан": ["Крыса"],
    "рэпчик": ["Рэп"],
    "сабка": ["Саб"],
    "сасмейт": ["Сас"],
    "селеба": ["Селебрити"],
    "слопик": ["Слоп"],
    "смешняк": ["Смех"],
    "соцфоб": ["Социофобия"],
    "срачик": ["Срач"],
    "сычик": ["Сыч"],
    "твича": ["Twitch"],
    "тиккун": ["Тик"],
    "трапик": ["Трап"],
    "трапчик": ["Трап"],
    "трукрайм": ["True crime", "Криминал"],
    "фейкер": ["Фейк"],
    "хайпан": ["Хайп"],
    "хайпмейк": ["Хайп"],
    "хайпожор": ["Хайп"],
    "хардбас": ["Hardbass", "Хардбас"],
    "шкурка": ["Шкур"],
    "шкурник": ["Шкур"],
    "шортс": ["Shorts"],
    "юморок": ["Юмор"],
    "ядерка": ["Ядерка"],
    "авито": ["Авито"],
    "бекап": ["Бэкап"],
    "бустер": ["Бустер"],
    "взлом": ["Взлом"],
    "вирус": ["Вирус"],
    "гифка": ["GIF"],
    "доксер": ["Доксинг"],
    "крекер": ["Крекер"],
    "малвар": ["Вредоносное ПО"],
    "руткит": ["Руткит"],
    "сватер": ["Сваттинг"],
    "троян": ["Троян"],
    "читкод": ["Чит"],
    "телега": ["Telegram"],
    "скилл": ["Skill"],
    "ютубер": ["YouTube"],
}


def search_titles(query: str, limit: int = 6) -> list[str]:
    try:
        data = api(action="query", list="search", srsearch=query, srlimit=limit)
    except Exception:
        return []
    return [h["title"] for h in data.get("query", {}).get("search", [])]


def score_match(
    word: str,
    title: str,
    extract: str,
    *,
    mapped: bool,
    explicit: bool = False,
    query_title: str | None = None,
) -> int:
    w = normalize(word)
    t = normalize(title)
    e = normalize(extract[:800] if extract else "")
    score = 0
    if mapped:
        score += 8
    if explicit:
        score += 10
    if query_title and titles_close(word, query_title):
        score += 8
    if t == w:
        score += 12
    elif titles_close(word, title):
        score += 9
    elif w in t.split():
        score += 10
    elif w in t:
        score += 7
    if w in e:
        score += 4
    if normalize(title) in BAD_IMAGE_TITLES:
        return -10
    if any(x in title.lower() for x in ("обсуждение", "архив", "копипаста:", "старая версия")):
        score -= 6
    if len(title) > len(word) * 4 and w not in t and not explicit and not (query_title and titles_close(word, query_title)):
        score -= 4
    return score


def candidate_titles(word: str, title_index: dict[str, str]) -> list[tuple[str, bool]]:
    seen: set[str] = set()
    out: list[tuple[str, bool]] = []

    def add(t: str, explicit: bool = False) -> None:
        if t and t not in seen:
            seen.add(t)
            out.append((t, explicit))

    for t in guess_titles(word, title_index):
        add(t)
    for t in EXTRA_SEARCH.get(word, []):
        add(t, explicit=True)
    mapped = MEME_NEOLURK_TITLE_MAP.get(word)
    if mapped:
        add(mapped, explicit=True)
    for t in search_titles(word, 6):
        add(t)
    if word.endswith("чан") and len(word) > 5:
        add(word[:-3].capitalize())
    if word.endswith("фаг"):
        add(word[:-3].capitalize())
    return out


def resolve_image(word: str, title_index: dict[str, str]) -> tuple[dict | None, int]:
    best_art: dict | None = None
    best_score = 0
    mapped = word in MEME_NEOLURK_TITLE_MAP
    explicit_titles = set(EXTRA_SEARCH.get(word, []))
    if mapped:
        explicit_titles.add(MEME_NEOLURK_TITLE_MAP[word])

    for title, explicit in candidate_titles(word, title_index):
        art = fetch_article(title)
        time.sleep(0.04)
        if not art or not art.get("image"):
            continue
        if any(part in art["image"].lower() for part in BAD_IMAGE_URL_PARTS):
            continue
        is_explicit = explicit or title in explicit_titles or art["title"] in explicit_titles
        s = score_match(
            word,
            art["title"],
            art.get("extract", ""),
            mapped=mapped,
            explicit=is_explicit,
            query_title=title,
        )
        if s > best_score:
            best_score = s
            best_art = art
        if s >= 12:
            break

    min_score = 4 if mapped or word in EXTRA_SEARCH else 6
    if best_score < min_score:
        return None, best_score
    return best_art, best_score


def clean_bad_images(cache: dict) -> int:
    removed = 0
    for word in CURATED_DVACH_NOUNS:
        entry = cache.get(word, {})
        src = (entry.get("image_source") or entry.get("example_title") or "").lower()
        img = entry.get("image") or ""
        if any(bad in src or bad in img.lower() for bad in BAD_IMAGE_TITLES):
            entry.pop("image", None)
            entry.pop("image_source", None)
            removed += 1
            continue
        if any(part in img.lower() for part in BAD_IMAGE_URL_PARTS):
            entry.pop("image", None)
            entry.pop("image_source", None)
            removed += 1
    return removed


def main() -> None:
    cache = load_enrichment()
    removed = clean_bad_images(cache)
    if removed:
        print(f"Убрано ложных картинок: {removed}")
    title_index = load_title_index()
    missing = [w for w in sorted(CURATED_DVACH_NOUNS) if not cache.get(w, {}).get("image")]

    added: list[tuple[str, str, int]] = []
    failed: list[str] = []

    for i, word in enumerate(missing, 1):
        art, score = resolve_image(word, title_index)
        if not art:
            failed.append(word)
            continue
        entry = cache.setdefault(word, {})
        entry["image"] = art["image"]
        entry["image_source"] = art["url"]
        if not entry.get("example") and art.get("extract"):
            entry["example"] = first_sentence(art["extract"])
            entry["example_source"] = art["url"]
            entry["example_title"] = art["title"]
        added.append((word, art["title"], score))
        if i % 20 == 0:
            CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  … {i}/{len(missing)}", flush=True)

    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

    still = [w for w in CURATED_DVACH_NOUNS if not cache.get(w, {}).get("image")]
    report = {
        "added": [{"word": w, "title": t, "score": s} for w, t, s in added],
        "still_missing": still,
    }
    out = SCRIPTS.parent / "sources" / "meme-images-fill-report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Без картинки было: {len(missing)}")
    print(f"Добавлено: {len(added)}")
    print(f"Осталось без картинки: {len(still)}")
    print(f"→ {out}")


if __name__ == "__main__":
    main()
