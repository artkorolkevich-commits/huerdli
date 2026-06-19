#!/usr/bin/env python3
"""Собрать страницу ревью словарей (мат + двач/лурк) и markdown-справочник."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402
from dvach_definitions import DVACH_DEFINITIONS, missing_definitions as missing_dvach  # noqa: E402
from profanity_curated_data import CURATED_PROFANITY_NOUNS  # noqa: E402
from profanity_definitions import PROFANITY_DEFINITIONS, missing_definitions as missing_mat  # noqa: E402
from word_review_enrichment import CACHE_PATH, load_enrichment, sanitize_enrichment  # noqa: E402

OUT_HTML = ROOT / "public" / "profanity-review.html"
OUT_MD = ROOT / "sources" / "dictionary-review-with-definitions.md"

missing_mat_words = missing_mat(CURATED_PROFANITY_NOUNS)
missing_dvach_words = missing_dvach(CURATED_DVACH_NOUNS)
if missing_mat_words:
    raise SystemExit(f"Нет мат-определений: {missing_mat_words[:8]}")
if missing_dvach_words:
    raise SystemExit(f"Нет двач-определений: {missing_dvach_words[:8]}")


def word_entries(enrichment: dict[str, dict]) -> list[dict[str, str | int | list[str] | None]]:
    all_words = sorted(CURATED_PROFANITY_NOUNS | CURATED_DVACH_NOUNS)
    rows: list[dict[str, str | int | list[str] | None]] = []
    for word in all_words:
        sources: list[str] = []
        if word in CURATED_PROFANITY_NOUNS:
            sources.append("mat")
        if word in CURATED_DVACH_NOUNS:
            sources.append("dvach")

        defs: list[str] = []
        if "mat" in sources:
            defs.append(PROFANITY_DEFINITIONS[word])
        if "dvach" in sources:
            dv = DVACH_DEFINITIONS[word]
            if dv not in defs:
                defs.append(dv)

        extra = sanitize_enrichment(
            word,
            enrichment.get(word, {}),
            is_mat="mat" in sources,
            is_dvach="dvach" in sources,
        )
        image = extra.get("image")

        rows.append(
            {
                "word": word,
                "len": len(word),
                "sources": sources,
                "definition": " / ".join(defs),
                "example": extra.get("example"),
                "example_source": extra.get("example_source"),
                "example_title": extra.get("example_title"),
                "image": image,
                "image_source": extra.get("image_source") if image else None,
            }
        )
    return rows


def count_by_len(entries: list[dict], source: str | None = None) -> dict[int, int]:
    out: dict[int, int] = {}
    for e in entries:
        if source and source not in e["sources"]:
            continue
        ln = int(e["len"])
        out[ln] = out.get(ln, 0) + 1
    return out


def write_markdown(entries: list[dict[str, str | int | list[str]]]) -> None:
    mat_n = sum(1 for e in entries if "mat" in e["sources"])
    dv_n = sum(1 for e in entries if "dvach" in e["sources"])
    both = sum(1 for e in entries if len(e["sources"]) == 2)
    lines = [
        "# Словари Хуердли — ревью (мат + двач/лурк)",
        "",
        "- **Мат:** `scripts/profanity_curated_data.py`",
        "- **Двач/лурк:** `scripts/dvach_curated_data.py` (Неолурк, seed, дедупликация)",
        "",
        f"Всего уникальных слов: **{len(entries)}** (мат {mat_n}, двач {dv_n}, пересечение {both}).",
        "",
        "Интерактивное ревью: `public/profanity-review.html`.",
        "",
    ]
    for src, title in (("mat", "Матовый словарь"), ("dvach", "Двач / лурк")):
        subset = [e for e in entries if src in e["sources"]]
        c = count_by_len(subset)
        lines.append(f"## {title} ({len(subset)} слов)")
        lines.append("")
        for ln in (5, 6, 7, 8):
            if not c.get(ln):
                continue
            lines.append(f"### {ln} букв ({c[ln]})")
            lines.append("")
            for e in subset:
                if e["len"] != ln:
                    continue
                tags = "+".join(e["sources"])
                ex = ""
                if e.get("example"):
                    src = e.get("example_title") or "Неолурк"
                    ex = f' Пример ({src}): «{e["example"]}»'
                lines.append(f"- **{e['word'].upper()}** [{tags}] — {e['definition']}{ex}")
            lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_html(entries: list[dict[str, str | int | list[str]]]) -> None:
    mat_n = sum(1 for e in entries if "mat" in e["sources"])
    dv_n = sum(1 for e in entries if "dvach" in e["sources"])
    data_json = json.dumps(entries, ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ревью словарей — Хуердли</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #121213; --card: #1a1a1c; --border: #3a3a3c; --text: #fff;
      --muted: #a0a0a5; --accent: #538d4e; --danger: #b33a3a; --dvach: #5b7fb8;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.45; }}
    .wrap {{ max-width: 920px; margin: 0 auto; padding: 20px 16px 120px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.6rem; }}
    .lead {{ color: var(--muted); margin: 0 0 20px; }}
    .lead code {{ background: #2a2a2c; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 16px; position: sticky; top: 0; z-index: 5; background: rgba(18,18,19,.92); backdrop-filter: blur(8px); padding: 12px 0; border-bottom: 1px solid var(--border); }}
    .toolbar input[type="search"] {{ flex: 1 1 200px; min-width: 160px; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--text); font-size: 1rem; }}
    .toolbar button {{ padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--text); cursor: pointer; font: inherit; }}
    .toolbar button:hover {{ background: #2a2a2c; }}
    .toolbar button.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
    .filters {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .chip {{ padding: 6px 10px; border-radius: 999px; border: 1px solid var(--border); background: transparent; color: var(--muted); cursor: pointer; font-size: 0.9rem; }}
    .chip.active {{ border-color: var(--accent); color: #fff; background: rgba(83,141,78,.15); }}
    .stats {{ color: var(--muted); font-size: 0.95rem; margin-bottom: 12px; }}
    .stats strong {{ color: var(--text); }}
    .stats .marked {{ color: #ff8a8a; }}
    section h2 {{ font-size: 1rem; color: var(--muted); margin: 24px 0 10px; letter-spacing: .06em; text-transform: uppercase; }}
    .row {{ display: grid; grid-template-columns: 36px 110px 1fr; gap: 12px; align-items: start; padding: 12px; border: 1px solid var(--border); border-radius: 10px; background: var(--card); margin-bottom: 8px; }}
    .row.has-image {{ grid-template-columns: 36px 110px 1fr 140px; }}
    .row.marked {{ border-color: var(--danger); background: rgba(179,58,58,.08); }}
    .row input {{ width: 18px; height: 18px; margin-top: 4px; cursor: pointer; }}
    .word {{ font-weight: 700; font-size: 1.1rem; letter-spacing: .08em; }}
    .tags {{ margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }}
    .tag {{ font-size: .7rem; padding: 2px 6px; border-radius: 4px; font-weight: 600; letter-spacing: 0; }}
    .tag-mat {{ background: rgba(179,58,58,.25); color: #ffb4b4; }}
    .tag-dvach {{ background: rgba(91,127,184,.25); color: #b4cffb; }}
    .len {{ display: inline-block; font-size: .75rem; color: var(--muted); background: #2a2a2c; padding: 2px 6px; border-radius: 4px; margin-top: 4px; }}
    .def {{ color: #e8e8ea; }}
    .example {{ margin-top: 8px; font-size: .92rem; color: #c8c8cc; border-left: 3px solid #3a3a42; padding-left: 10px; }}
    .example q {{ font-style: italic; color: #dddde0; }}
    .example a {{ color: #8ab4f8; text-decoration: none; }}
    .example a:hover {{ text-decoration: underline; }}
    .meme {{ grid-row: span 2; align-self: start; }}
    .meme img {{ width: 100%; max-width: 140px; border-radius: 8px; border: 1px solid var(--border); background: #0e0e10; object-fit: contain; max-height: 140px; }}
    .meme a {{ display: block; font-size: .7rem; color: var(--muted); margin-top: 4px; text-align: center; }}
    .footer-bar {{ position: fixed; left: 0; right: 0; bottom: 0; background: rgba(18,18,19,.96); border-top: 1px solid var(--border); padding: 12px 16px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-items: center; }}
    .footer-bar .count {{ color: var(--muted); min-width: 200px; text-align: center; }}
    .footer-bar .count strong {{ color: #ff8a8a; }}
    .note {{ background: rgba(181,159,59,.12); border: 1px solid rgba(181,159,59,.35); border-radius: 10px; padding: 12px 14px; margin-bottom: 16px; font-size: .95rem; }}
    textarea.export {{ position: absolute; left: -9999px; opacity: 0; }}
    @media (max-width: 560px) {{ .row, .row.has-image {{ grid-template-columns: 32px 1fr; }} .word-block {{ grid-column: 2; }} .def, .meme {{ grid-column: 1 / -1; padding-left: 44px; }} .meme img {{ max-width: 100%; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Ревью словарей</h1>
    <p class="lead">
      <strong>Мат</strong> ({mat_n} слов, 5–6 букв) — <code>profanity_curated_data.py</code>, без обрезков.<br>
      <strong>Двач / лурк</strong> ({dv_n} слов, 5–8 букв) — Неолурк + seed, без множественного числа
      (если есть единственное) и без однобуквенных дублей (зэтник, не зетник).<br>
      Уникальных записей: <strong>{len(entries)}</strong>. Отметьте галочкой лишнее и скопируйте JSON.
    </p>
    <div class="note">
      Галочки сохраняются в браузере. В JSON у каждого слова указан словарь (<code>mat</code> / <code>dvach</code>).
    </div>
    <div class="toolbar">
      <input id="search" type="search" placeholder="Поиск…" autocomplete="off" />
      <div class="filters" id="filters">
        <button type="button" class="chip active" data-filter="all">Все</button>
        <button type="button" class="chip" data-filter="mat">Мат</button>
        <button type="button" class="chip" data-filter="dvach">Двач</button>
        <button type="button" class="chip" data-filter="5">5</button>
        <button type="button" class="chip" data-filter="6">6</button>
        <button type="button" class="chip" data-filter="7">7</button>
        <button type="button" class="chip" data-filter="8">8</button>
        <button type="button" class="chip" data-filter="marked">Отмеченные</button>
      </div>
      <button type="button" id="clear-marks">Снять галочки</button>
    </div>
    <p class="stats" id="stats"></p>
    <div id="list"></div>
  </div>
  <div class="footer-bar">
    <span class="count" id="footer-count">Отмечено: <strong>0</strong></span>
    <button type="button" class="primary" id="copy-rejected">Скопировать JSON</button>
    <button type="button" id="download-rejected">Скачать JSON</button>
  </div>
  <textarea id="export-area" class="export" aria-hidden="true"></textarea>
  <script>
    const ENTRIES = {data_json};
    const STORAGE_KEY = "huerdli-dictionary-reject-v2";
    const listEl = document.getElementById("list");
    const searchEl = document.getElementById("search");
    const statsEl = document.getElementById("stats");
    const footerCountEl = document.getElementById("footer-count");
    const exportArea = document.getElementById("export-area");
    let rejected = new Map(Object.entries(JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}")));
    let activeFilter = "all";

    function save() {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Object.fromEntries(rejected)));
    }}

    function rejectKey(entry) {{
      return entry.word + ":" + entry.sources.join("+");
    }}

    function isMarked(entry) {{
      return rejected.has(rejectKey(entry));
    }}

    function updateCounts(visible) {{
      statsEl.innerHTML = `Показано: <strong>${{visible}}</strong> из ${{ENTRIES.length}} · Отмечено: <span class="marked"><strong>${{rejected.size}}</strong></span>`;
      footerCountEl.innerHTML = `Отмечено: <strong>${{rejected.size}}</strong>`;
    }}

    function matches(entry) {{
      const q = searchEl.value.trim().toLowerCase();
      if (q && !entry.word.includes(q) && !entry.definition.toLowerCase().includes(q)) return false;
      if (activeFilter === "marked") return isMarked(entry);
      if (activeFilter === "mat") return entry.sources.includes("mat");
      if (activeFilter === "dvach") return entry.sources.includes("dvach");
      if (["5","6","7","8"].includes(activeFilter)) return String(entry.len) === activeFilter;
      return true;
    }}

    function sourceTags(sources) {{
      return sources.map(s => `<span class="tag tag-${{s}}">${{s === "mat" ? "мат" : "двач"}}</span>`).join("");
    }}

    function esc(s) {{
      return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");
    }}

    function exampleHtml(entry) {{
      if (!entry.example) return "";
      const title = entry.example_title ? esc(entry.example_title) : "Неолурк";
      const link = entry.example_source ? `<a href="${{esc(entry.example_source)}}" target="_blank" rel="noopener">${{title}}</a>` : title;
      return `<div class="example"><q>${{esc(entry.example)}}</q> — ${{link}}</div>`;
    }}

    function memeHtml(entry) {{
      if (!entry.image) return "";
      const src = esc(entry.image);
      const href = esc(entry.image_source || entry.image);
      return `<div class="meme"><a href="${{href}}" target="_blank" rel="noopener"><img src="${{src}}" alt="" loading="lazy" /></a></div>`;
    }}

    function render() {{
      listEl.innerHTML = "";
      let visible = 0;
      let currentLen = null;
      for (const entry of ENTRIES.filter(matches)) {{
        visible++;
        if (entry.len !== currentLen) {{
          currentLen = entry.len;
          const h = document.createElement("section");
          h.innerHTML = `<h2>${{entry.len}} букв</h2>`;
          listEl.appendChild(h);
        }}
        const key = rejectKey(entry);
        const row = document.createElement("label");
        const hasMeme = !!entry.image;
        row.className = "row" + (isMarked(entry) ? " marked" : "") + (hasMeme ? " has-image" : "");
        row.innerHTML = `
          <input type="checkbox" ${{isMarked(entry) ? "checked" : ""}} />
          <div class="word-block">
            <div class="word">${{entry.word.toUpperCase()}}</div>
            <span class="len">${{entry.len}} букв</span>
            <div class="tags">${{sourceTags(entry.sources)}}</div>
          </div>
          <div class="def">${{esc(entry.definition)}}${{exampleHtml(entry)}}</div>
          ${{hasMeme ? memeHtml(entry) : ""}}`;
        const cb = row.querySelector("input");
        cb.addEventListener("change", () => {{
          if (cb.checked) rejected.set(key, {{ word: entry.word, sources: entry.sources }});
          else rejected.delete(key);
          save(); render();
        }});
        listEl.appendChild(row);
      }}
      updateCounts(visible);
    }}

    function exportRejected() {{
      const items = [...rejected.values()].sort((a,b) => a.word.localeCompare(b.word));
      return JSON.stringify({{ source: "dictionary-review", rejected: items, count: items.length, total: ENTRIES.length }}, null, 2);
    }}

    document.getElementById("copy-rejected").addEventListener("click", async () => {{
      const text = exportRejected();
      exportArea.value = text;
      try {{ await navigator.clipboard.writeText(text); alert(`Скопировано ${{rejected.size}} позиций`); }}
      catch {{ exportArea.select(); document.execCommand("copy"); alert("Скопировано"); }}
    }});
    document.getElementById("download-rejected").addEventListener("click", () => {{
      const blob = new Blob([exportRejected()], {{ type: "application/json" }});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "dictionary-rejected.json";
      a.click();
      URL.revokeObjectURL(a.href);
    }});
    document.getElementById("clear-marks").addEventListener("click", () => {{
      if (!rejected.size || confirm("Снять все галочки?")) {{ rejected = new Map(); save(); render(); }}
    }});
    searchEl.addEventListener("input", render);
    document.getElementById("filters").addEventListener("click", (e) => {{
      const btn = e.target.closest(".chip");
      if (!btn) return;
      activeFilter = btn.dataset.filter;
      document.querySelectorAll(".chip").forEach(c => c.classList.toggle("active", c === btn));
      render();
    }});
    render();
  </script>
</body>
</html>"""
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> None:
    if not CACHE_PATH.exists():
        print("Нет кэша примеров — запустите: .venv/bin/python scripts/word_review_enrichment.py")
    enrichment = load_enrichment()
    entries = word_entries(enrichment)
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(entries)
    write_html(entries)
    print(f"  {OUT_HTML.relative_to(ROOT)}")
    print(f"  {OUT_MD.relative_to(ROOT)}")
    print(f"  {len(entries)} уникальных слов (мат {len(CURATED_PROFANITY_NOUNS)}, двач {len(CURATED_DVACH_NOUNS)})")
    with_ex = sum(1 for e in entries if e.get("example"))
    with_img = sum(1 for e in entries if e.get("image"))
    print(f"  примеров: {with_ex}, картинок: {with_img}")


if __name__ == "__main__":
    main()
