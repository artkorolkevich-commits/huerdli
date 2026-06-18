#!/usr/bin/env python3
"""Дописать недостающие определения в dvach_definitions.py."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from dvach_curated_data import CURATED_DVACH_NOUNS  # noqa: E402
from dvach_definitions import DVACH_DEFINITIONS  # noqa: E402
from profanity_definitions import PROFANITY_DEFINITIONS  # noqa: E402


def auto_define(word: str) -> str:
    if word in PROFANITY_DEFINITIONS:
        return PROFANITY_DEFINITIONS[word]

    if word.endswith("срач"):
        topic = word[:-4]
        return f"Срач (массовая перепалка) на тему «{topic}» на имиджборде."
    if word.endswith("фаг"):
        stem = word[:-3]
        return f"Фанат/завсегдатай темы «{stem}» в интернет-сленге."
    if word.endswith("чан"):
        return f"Пользователь имиджборды «{word[:-3]}» или раздела с таким названием."
    if word.endswith("тян"):
        return f"Мем-персонаж -тян; интернет-типаж с имиджбордов."
    if word.endswith("кун"):
        return f"Мем-персонаж -кун; интернет-типаж с имиджбордов."
    if word.startswith("говно"):
        return f"Мемный термин на тему «говна» в интернет-культуре: {word}."
    if word.startswith("двач"):
        return f"Термин культуры Двача/имиджбордов: {word}."
    if word.startswith("лурк"):
        return f"Термин энциклопедии Луркоморье или её сообщества: {word}."
    if word.startswith("мем"):
        return f"Мемный термин рунета: {word}."
    if word.startswith("анон"):
        return f"Термин анонимного имиджборда: {word}."
    if word.startswith("битард"):
        return f"Термин субкультуры /b/-битарда: {word}."
    if word.endswith("борд"):
        return f"Имиджборд или его раздел в интернет-сленге: {word}."
    if "фаг" in word:
        return f"Интернет-сленг на тему фанатства/субкультуры: {word}."
    return f"Интернет-лексика рунета/имиджбордов: {word}."


def main() -> None:
    missing = sorted(w for w in CURATED_DVACH_NOUNS if w not in DVACH_DEFINITIONS)
    if not missing:
        print("Все определения на месте.")
        return

    path = SCRIPTS / "dvach_definitions.py"
    text = path.read_text(encoding="utf-8")
    insert_at = text.rfind("}")
    if insert_at < 0:
        raise SystemExit("Не найден конец словаря DVACH_DEFINITIONS")

    additions = []
    for word in missing:
        definition = auto_define(word).replace("\\", "\\\\").replace('"', '\\"')
        additions.append(f'    "{word}": "{definition}",')

    new_block = "\n".join(additions) + "\n"
    updated = text[:insert_at] + new_block + text[insert_at:]
    path.write_text(updated, encoding="utf-8")
    print(f"Добавлено {len(missing)} определений → {path.name}")


if __name__ == "__main__":
    main()
