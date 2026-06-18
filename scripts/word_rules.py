"""
Критерии отбора слов для словарей «Хуердли».

Каждое слово в игре должно быть реальной единицей русской лексики:
его можно найти в словаре, объяснить смысл и понять без догадок.
Мат, оскорбления и обычная лексика проходят одни и те же правила качества;
различается только источник списка (автоматический / ручной).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymorphy2

CYRILLIC_WORD = re.compile(r"^[а-яё]+$")

# Редкие, но грамматически «настоящие» формы, которые не подходят для игры:
# архаизмы без современного смысла, имена, обрывки, опечатки источника.
BLOCKLIST: frozenset[str] = frozenset({
    "абшид", "абцуг", "адряс", "алчба", "ажгон", "яхонт",
    "айеайе", "акание", "акароз", "аларма", "анатом", "антре", "ахание",
    "бердан", "бибабо", "бонмо", "бутада",
})

# Обрезанные формы, которые сами по себе не являются словами (только для матового списка).
PROFANITY_FRAGMENT_DENYLIST: frozenset[str] = frozenset({
    "вырод", "долбо", "мерзо", "подон", "скотин", "сучон", "ублюд",
    "лохуш", "выбляд", "мудач", "наебос", "фигвам", "сифил", "шалав",
})

DICTIONARY_RULES = """
# Правила отбора слов для «Хуердли»

## Цель

В словаре только слова, которые **существуют в русской лексике** и **имеют
понятный смысл** — их можно объяснить одним предложением, даже если слово
редкое, грубое или устаревшее. Мат и оскорбления допустимы наравне с
нейтральной лексикой; важно качество слова, а не его вежливость.

## Общие требования (оба словаря)

1. **Длина** — 5 или 6 букв (после приведения Ё → Е). Для расширенных
   списков допускается 7 букв, но в игру попадают только 5 и 6.
2. **Алфавит** — только кириллица, без латиницы, цифр и дефисов.
3. **Самостоятельное слово** — не обрывок, не аббревиатура, не слияние
   двух слов ради длины (например, «фигвам» ← «фиг вам»).
4. **Часть речи** — существительное в словарной форме или устойчивая
   субстантивированная форма, которую носитель узнаёт как слово.
5. **Объяснимость** — у слова есть значение в толковом или сленговом
   словаре; игрок может понять, *что* это, а не только *как* написать.
6. **Не имя собственное** — личные имена, редкие топонимы и фамилии
   исключаются, если нет общеупотребительного значения (кошка ✓, гамлет ✗).

## Обычный словарь (`ru-nouns-*.txt`)

Источник: [Harrix/Russian-Nouns](https://github.com/Harrix/Russian-Nouns).

Слово попадает в словарь, если:

- есть в исходном списке существительных;
- pymorphy2 распознаёт хотя бы одну форму как `NOUN` (не `UNKN`);
- среди разборов есть **не** имя/фамилия (`Name`, `Surn`);
- слово не в ручном `BLOCKLIST` (архаизмы и артефакты источника).

Отсекаются: частицы («авось»), прилагательные, глаголы, междометия,
чистые имена собственные, неразбираемые строки.

## Матовый словарь (`ru-profanity-nouns-*.txt`)

Источник: ручной curated-список `scripts/profanity_curated_data.py`.

К общим правилам добавляются:

- слово должно быть **узнаваемым** матом, ругательством, обзывательством
  или грубым существительным (включая эвфемизмы вроде «нафиг», «фигня»);
- **запрещены обрезки** длинных форм ради 5–6 букв
  (например, «долбо» ← «долбоёб», «подон» ← «подонок»);
- предпочтение полным лексемам: «шалава», а не «шалав»;
- каждое добавление проверяется вручную по смыслу и самостоятельности.

## Процесс обновления

```bash
.venv/bin/python scripts/build_dictionaries.py
npm run dict:sync
```

Скрипт сборки применяет `word_rules.py` и падает с ошибкой, если матовых
слов меньше минимума или curated-список нарушает правила.
"""


def normalize(word: str) -> str:
    word = word.strip().lower().replace("ё", "е")
    return re.sub(r"[^а-я]", "", word)


def is_valid_shape(word: str, lengths: tuple[int, ...] = (5, 6)) -> bool:
    w = normalize(word)
    return bool(w) and len(w) in lengths and bool(CYRILLIC_WORD.match(word.strip().lower()))


def noun_parses(morph: pymorphy2.MorphAnalyzer, word: str) -> list:
    return [
        p for p in morph.parse(word)
        if "NOUN" in str(p.tag) and "UNKN" not in str(p.tag)
    ]


def is_common_noun(morph: pymorphy2.MorphAnalyzer, word: str) -> bool:
    """Существительное общей лексики, не чистое имя собственное."""
    parses = noun_parses(morph, word)
    if not parses:
        return False
    common = [p for p in parses if "Name" not in str(p.tag) and "Surn" not in str(p.tag)]
    return bool(common)


GUESS_EXTENDED_LENGTHS: tuple[int, ...] = (7, 8)


def passes_guess_extended_rules(word: str) -> bool:
    """Слова 7–8 букв только для ввода: максимум охвата, без строгого NOUN-фильтра."""
    w = normalize(word)
    if not w or len(w) not in GUESS_EXTENDED_LENGTHS:
        return False
    if w in BLOCKLIST:
        return False
    return bool(re.fullmatch(r"[а-я]+", w))


def reject_reason_guess_extended(word: str) -> str | None:
    w = normalize(word)
    if not w:
        return "пустое"
    if len(w) not in GUESS_EXTENDED_LENGTHS:
        return "неверная длина"
    if w in BLOCKLIST:
        return "blocklist"
    if not re.fullmatch(r"[а-я]+", w):
        return "не кириллица"
    return None


def passes_normal_dictionary_rules(morph: pymorphy2.MorphAnalyzer, word: str) -> bool:
    w = normalize(word)
    if not w or w in BLOCKLIST:
        return False
    return is_common_noun(morph, w)


def reject_reason_normal(morph: pymorphy2.MorphAnalyzer, word: str) -> str | None:
    w = normalize(word)
    if not w:
        return "пустое"
    if w in BLOCKLIST:
        return "blocklist"
    if not noun_parses(morph, w):
        return "нет разбора NOUN"
    if not is_common_noun(morph, w):
        return "имя собственное / фамилия"
    return None


def passes_profanity_rules(word: str) -> bool:
    w = normalize(word)
    if not is_valid_shape(w):
        return False
    if w in PROFANITY_FRAGMENT_DENYLIST:
        return False
    return True


def reject_reason_profanity(word: str) -> str | None:
    w = normalize(word)
    if not w:
        return "пустое"
    if not is_valid_shape(w):
        return "неверная длина или алфавит"
    if w in PROFANITY_FRAGMENT_DENYLIST:
        return "обрезанная форма"
    return None


# Обрезки для двач-словаря.
DVACH_FRAGMENT_DENYLIST: frozenset[str] = frozenset({
    "фигвам", "шалав",
})

DVACH_LENGTHS: tuple[int, ...] = (5, 6, 7, 8)


def passes_dvach_rules(word: str) -> bool:
    """Интернет-лексика: форма 5–8 букв, кириллица, не обрывок."""
    w = normalize(word)
    if not is_valid_shape(w, DVACH_LENGTHS):
        return False
    if w in DVACH_FRAGMENT_DENYLIST:
        return False
    return True


def reject_reason_dvach(word: str) -> str | None:
    w = normalize(word)
    if not w:
        return "пустое"
    if not is_valid_shape(w, DVACH_LENGTHS):
        return "неверная длина или алфавит"
    if w in DVACH_FRAGMENT_DENYLIST:
        return "обрезанная форма"
    return None
