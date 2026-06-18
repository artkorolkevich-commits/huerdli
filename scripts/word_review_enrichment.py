#!/usr/bin/env python3
"""Примеры употребления и картинки мемов из Неолурка для дашборда ревью."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402
from profanity_curated_data import CURATED_PROFANITY_NOUNS  # noqa: E402
from word_rules import normalize  # noqa: E402
from meme_review_overrides import (  # noqa: E402
    MEME_NEOLURK_TITLE_MAP,
    MEME_REVIEW_OVERRIDES,
    MEME_RELATED_NEOLURK_SEARCH,
)

NEOLURK_API = "https://lurkmore.org/w/api.php"
WIKI_BASE = "https://lurkmore.org/wiki/"
UA = {"User-Agent": "HuerdliDictionaryBuilder/1.0"}
CACHE_PATH = SOURCES / "word_review_enrichment.json"

STRIP_RE = re.compile(r"<[^>]+>")


def api(**params) -> dict:
    url = NEOLURK_API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read())


def load_title_index() -> dict[str, str]:
    path = SOURCES / "neolurk_titles.txt"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        title = line.strip()
        if title:
            out[normalize(title)] = title
    return out


def clean_html(text: str) -> str:
    text = unescape(STRIP_RE.sub("", text))
    return re.sub(r"\s+", " ", text).strip()


def first_sentence(text: str, limit: int = 220) -> str:
    text = text.strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?…])\s+", text)
    out = parts[0]
    if len(out) < 40 and len(parts) > 1:
        out = f"{parts[0]} {parts[1]}"
    if len(out) > limit:
        out = out[: limit - 1].rsplit(" ", 1)[0] + "…"
    return out


def guess_titles(word: str, title_index: dict[str, str]) -> list[str]:
    w = normalize(word)
    titles: list[str] = []
    if w in MEME_NEOLURK_TITLE_MAP:
        titles.append(MEME_NEOLURK_TITLE_MAP[w])
    if w in title_index:
        titles.append(title_index[w])
    cap = w[:1].upper() + w[1:] if w else w
    if cap not in titles:
        titles.append(cap)
    if w.upper() not in titles and len(w) <= 8:
        titles.append(w.upper())
    return titles


def fetch_image_from_wikitext(title: str) -> str | None:
    try:
        data = api(action="parse", page=title, prop="text", redirects=1)
        html = data["parse"]["text"]["*"]
    except Exception:
        return None
    for m in re.finditer(r'(?:src|href)="(/w/images/[^"]+)"', html):
        path = m.group(1)
        if "/thumb/" in path:
            path = re.sub(r"/thumb/(.+)/\d+px-[^/]+$", r"/\1", path)
        if any(x in path.lower() for x in ("icon", "button", "logo")):
            continue
        if path.endswith(".svg"):
            continue
        return "https://neolurk.org" + path
    return None


def fetch_article(title: str) -> dict | None:
    try:
        data = api(
            action="query",
            titles=title,
            prop="extracts|pageimages|info",
            exintro=1,
            explaintext=1,
            redirects=1,
            piprop="original|thumbnail",
            pithumbsize=480,
            inurl=1,
        )
    except Exception:
        return None
    resolved_title = title
    for redir in data.get("query", {}).get("redirects", []):
        if redir.get("from") == title or normalize(redir.get("from", "")) == normalize(title):
            resolved_title = redir.get("to", title)
    for page in data.get("query", {}).get("pages", {}).values():
        if page.get("missing"):
            continue
        extract = page.get("extract", "").strip()
        image = None
        if "original" in page:
            image = page["original"].get("source")
        elif "thumbnail" in page:
            image = page["thumbnail"].get("source")
        page_title = page.get("title", resolved_title)
        if not image:
            image = fetch_image_from_wikitext(page_title)
        url = page.get("fullurl") or (WIKI_BASE + urllib.parse.quote(page_title.replace(" ", "_")))
        return {
            "title": page.get("title", resolved_title),
            "extract": extract,
            "image": image,
            "url": url,
        }
    return None


def fetch_search_snippet(word: str) -> dict | None:
    try:
        data = api(action="query", list="search", srsearch=f'"{word}"', srlimit=8, srwhat="text")
    except Exception:
        return None
    hits = data.get("query", {}).get("search", [])
    w = normalize(word)
    best = None
    for hit in hits:
        snippet = clean_html(hit.get("snippet", ""))
        title = hit.get("title", "")
        if not snippet and not title:
            continue
        text = snippet or title
        score = 0
        if w in normalize(text):
            score += 2
        if w in normalize(title):
            score += 3
        if "обсуждение" in title.lower() or "архив" in title.lower():
            score -= 1
        if best is None or score > best[0]:
            best = (score, title, snippet or title, hit)
    if not best:
        return None
    _, title, snippet, hit = best
    url = WIKI_BASE + urllib.parse.quote(title.replace(" ", "_"))
    return {"title": title, "snippet": snippet, "url": url}


def apply_overrides(word: str, entry: dict[str, str | None], *, dvach: bool) -> dict[str, str | None]:
    override = MEME_REVIEW_OVERRIDES.get(word)
    if not override:
        return entry
    for key, value in override.items():
        if key == "image" and not dvach:
            continue
        if value:
            entry[key] = value
    return entry


def enrich_word(word: str, *, dvach: bool, title_index: dict[str, str]) -> dict:
    entry: dict[str, str | None] = {
        "example": None,
        "example_source": None,
        "example_title": None,
        "image": None,
        "image_source": None,
    }

    article = None
    for title in guess_titles(word, title_index):
        article = fetch_article(title)
        time.sleep(0.08)
        if article and article.get("extract"):
            break
        if article and article.get("image") and dvach:
            break

    if article and article.get("extract"):
        entry["example"] = first_sentence(article["extract"])
        entry["example_source"] = article["url"]
        entry["example_title"] = article["title"]
        if dvach and article.get("image"):
            entry["image"] = article["image"]
            entry["image_source"] = article["url"]
        return apply_overrides(word, entry, dvach=dvach)

    search = fetch_search_snippet(word)
    time.sleep(0.08)
    if search and search.get("snippet"):
        entry["example"] = first_sentence(search["snippet"])
        entry["example_source"] = search["url"]
        entry["example_title"] = search["title"]

    if not entry.get("example"):
        related = MEME_RELATED_NEOLURK_SEARCH.get(word)
        if related:
            article = fetch_article(related)
            time.sleep(0.08)
            if article and article.get("extract"):
                entry["example"] = first_sentence(article["extract"])
                entry["example_source"] = article["url"]
                entry["example_title"] = article["title"]
                if dvach and article.get("image") and not entry.get("image"):
                    entry["image"] = article["image"]
                    entry["image_source"] = article["url"]

    return apply_overrides(word, entry, dvach=dvach)


def load_enrichment() -> dict[str, dict]:
    cache: dict[str, dict] = {}
    if CACHE_PATH.exists():
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    for word, override in MEME_REVIEW_OVERRIDES.items():
        merged = dict(cache.get(word, {}))
        for key, value in override.items():
            if value:
                merged[key] = value
        cache[word] = merged
    return cache


def build_enrichment(*, refresh: bool = False, limit: int | None = None) -> dict[str, dict]:
    cache: dict[str, dict] = {}
    if CACHE_PATH.exists() and not refresh:
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    title_index = load_title_index()
    all_words = sorted(CURATED_PROFANITY_NOUNS | CURATED_DVACH_NOUNS)
    if limit:
        all_words = all_words[:limit]

    updated = 0
    for i, word in enumerate(all_words, 1):
        if word in cache and cache[word].get("example") and not refresh:
            continue
        dvach = word in CURATED_DVACH_NOUNS
        cache[word] = enrich_word(word, dvach=dvach, title_index=title_index)
        updated += 1
        if updated % 25 == 0:
            CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  … {i}/{len(all_words)}", flush=True)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    with_example = sum(1 for v in cache.values() if v.get("example"))
    with_image = sum(1 for w, v in cache.items() if v.get("image") and w in CURATED_DVACH_NOUNS)
    print(f"Обогащено: {updated} новых запросов, примеров {with_example}/{len(all_words)}, картинок {with_image}")
    return cache


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="перезапросить все слова")
    parser.add_argument("--limit", type=int, default=None, help="только первые N слов (отладка)")
    args = parser.parse_args()
    build_enrichment(refresh=args.refresh, limit=args.limit)


if __name__ == "__main__":
    main()
