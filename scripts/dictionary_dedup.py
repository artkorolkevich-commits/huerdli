"""Дедупликация словарных списков: множественное число и варианты написания."""

from __future__ import annotations

from typing import TYPE_CHECKING

from word_rules import normalize

if TYPE_CHECKING:
    import pymorphy2

# Пары, где оба варианта осознанно оставляем (разный смысл).
SPELLING_VARIANT_KEEP_BOTH: frozenset[frozenset[str]] = frozenset({
    frozenset({"бумер", "зумер"}),
    frozenset({"вайпер", "хайпер"}),
    frozenset({"двачек", "двачер"}),
    frozenset({"лоликон", "лоликун"}),
    frozenset({"роглик", "рофлик"}),
    frozenset({"тайпан", "хайпан"}),
    frozenset({"трапик", "тралик"}),
    frozenset({"трапик", "трапчик"}),
    frozenset({"фотожаба", "фотожоп"}),
    frozenset({"рунет", "кунет"}),
    frozenset({"троль", "тролл"}),
    frozenset({"лолчто", "лолшто"}),
    frozenset({"мемчик", "мемпик"}),
    frozenset({"репост", "репорт"}),
    frozenset({"спамер", "скамер"}),
    frozenset({"хиккач", "хиккан"}),
    frozenset({"гейминг", "шейминг"}),
    frozenset({"неймфаг", "нэймфаг"}),
    frozenset({"нульчан", "нольчан"}),
    frozenset({"вебкам", "вебка"}),
})

# Проигравший вариант → предпочтительный (оставляем значение).
PREFERRED_SPELLING: dict[str, str] = {
    "зетник": "зэтник",
    "репчик": "рэпчик",
    "чатик": "чятик",
    "лолчто": "лолшто",
}

# Явные пары множественное → единственное для сленга, который pymorphy плохо ловит.
SLANG_PLURAL_TO_SINGULAR: dict[str, str] = {
    "аноны": "аноним",
    "блядки": "блядка",
    "бляди": "блядь",
    "гифки": "гифка",
    "донаты": "донат",
    "инцелы": "инцел",
    "кексы": "кекс",
    "кринжа": "кринж",
    "омежки": "омежка",
    "пидоры": "пидор",
    "скуфы": "скуф",
    "срачи": "срач",
    "тролли": "тролль",
    "иимемы": "иимем",
    "говноеды": "говноед",
    "приколы": "прикол",
    "шортсы": "шортс",
    "челики": "челик",
}

# Множественные формы не берём в словарь (см. drop_plural_forms).
PLURAL_FORM_DENYLIST: frozenset[str] = frozenset(SLANG_PLURAL_TO_SINGULAR.keys())


def one_letter_difference(a: str, b: str) -> bool:
    if len(a) != len(b) or a == b:
        return False
    diff = sum(1 for x, y in zip(a, b) if x != y)
    return diff == 1


def singular_candidates(word: str, morph: pymorphy2.MorphAnalyzer) -> set[str]:
    w = normalize(word)
    out: set[str] = set()

    if w in SLANG_PLURAL_TO_SINGULAR:
        out.add(SLANG_PLURAL_TO_SINGULAR[w])

    for parse in morph.parse(w):
        tag = str(parse.tag)
        if "NOUN" not in tag:
            continue
        if "plur" in tag:
            out.add(normalize(parse.normal_form))
        if "gent" in tag and word.endswith("а"):
            # кринжа → кринж
            out.add(normalize(parse.normal_form))

    # Эвристики для интернет-множественного
    if w.endswith("ки") and len(w) > 5:
        out.add(w[:-2] + "ка")
    if w.endswith("ы") and len(w) > 5:
        out.add(w[:-1])
    if w.endswith("и") and len(w) > 5:
        out.add(w[:-1] + "ь")
        out.add(w[:-1])

    return {c for c in out if c and c != w}


def drop_plural_forms(
    words: set[str],
    morph: pymorphy2.MorphAnalyzer,
) -> tuple[set[str], set[str]]:
    """Убрать множественные формы: из denylist и если единственное уже в наборе."""
    removed: set[str] = set()
    kept = set(words)
    for w in sorted(words):
        if w in PLURAL_FORM_DENYLIST:
            removed.add(w)
            kept.discard(w)
            continue
        parses = morph.parse(w)
        if parses:
            best = max(parses, key=lambda p: p.score)
            tag = str(best.tag)
            if (
                "NOUN" in tag
                and "plur" in tag
                and best.score >= 0.5
                and (w.endswith("ы") or w.endswith("и") or (w.endswith("а") and "gent" in tag))
            ):
                removed.add(w)
                kept.discard(w)
                continue
        for sing in singular_candidates(w, morph):
            if sing in words and frozenset({w, sing}) not in SPELLING_VARIANT_KEEP_BOTH:
                removed.add(w)
                kept.discard(w)
                break
    return kept, removed


def pick_spelling_variant(a: str, b: str) -> str:
    """Какой из двух однобуквенных вариантов оставить."""
    if a in PREFERRED_SPELLING and PREFERRED_SPELLING[a] == b:
        return b
    if b in PREFERRED_SPELLING and PREFERRED_SPELLING[b] == a:
        return b
    if a in PREFERRED_SPELLING.values():
        return a
    if b in PREFERRED_SPELLING.values():
        return b
    # Интернет-сленг: чаще пишут через «э»
    for ca, cb in zip(a, b):
        if ca != cb:
            if {ca, cb} == {"е", "э"}:
                return a if ca == "э" else b
            break
    return min(a, b)


def drop_one_letter_spelling_variants(words: set[str]) -> tuple[set[str], set[str]]:
    """Убрать варианты с тем же смыслом, отличающиеся одной буквой."""
    removed: set[str] = set()
    kept = set(words)
    sorted_words = sorted(words)
    for i, a in enumerate(sorted_words):
        if a not in kept:
            continue
        for b in sorted_words[i + 1 :]:
            if b not in kept:
                continue
            if not one_letter_difference(a, b):
                continue
            if frozenset((a, b)) in SPELLING_VARIANT_KEEP_BOTH:
                continue
            winner = pick_spelling_variant(a, b)
            loser = b if winner == a else a
            removed.add(loser)
            kept.discard(loser)
    return kept, removed


def deduplicate_dvach_words(
    words: set[str],
    morph: pymorphy2.MorphAnalyzer,
) -> tuple[set[str], dict[str, str]]:
    """Полная дедупликация двач-списка. Возвращает слова и причины удаления."""
    reasons: dict[str, str] = {}
    current = set(words)

    after_plural, plural_removed = drop_plural_forms(current, morph)
    for w in plural_removed:
        reasons[w] = "множественное число (есть единственное)"
    current = after_plural

    after_spell, spell_removed = drop_one_letter_spelling_variants(current)
    for w in spell_removed:
        reasons[w] = "вариант написания (отличается одной буквой)"
    current = after_spell

    return current, reasons
