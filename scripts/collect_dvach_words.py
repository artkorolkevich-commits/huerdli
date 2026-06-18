#!/usr/bin/env python3
"""Сбор словаря двача из Неолурка, бордословаря, ручного seed и интернет-лексики."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import pymorphy2
except ImportError:
    print("pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from word_rules import DVACH_LENGTHS, is_valid_shape, normalize  # noqa: E402
from dictionary_dedup import PLURAL_FORM_DENYLIST, deduplicate_dvach_words  # noqa: E402

NEOLURK_API = "https://lurkmore.org/w/api.php"
UA = {"User-Agent": "HuerdliDictionaryBuilder/1.0"}

MIN_DVACH_WORDS = 280

# Ложные срабатывания из заголовков Неолурка (7–8 букв).
NEOLURK_FALSE_POSITIVES: frozenset[str] = frozenset({
    "астролог", "аэрофлот", "карфаген", "венчание", "галичане", "еврогейм",
    "мемориал", "меметика", "анякунда", "волчанка", "волчанск", "блястяще",
})

# Слова, которые не берём в словарь (решение автора + dictionary-rejected.json).
USER_REJECTED: frozenset[str] = frozenset({
    "абибас",
    "абучан",
    "автосрач",
    "анимуфаг",
    "апачан",
    "арткор",
    "барафаг",
    "битардка",
    "битардск",
    "богосрач",
    "бырпкун",
    "блячь",
    "вайпер",
    "волкофаг",
    "воровчан",
    "говноеды",
    "говнокор",
    "гогисрач",
    "гомосрак",
    "гуротян",
    "двачую",
    "деегр",
    "задротов",
    "залго",
    "залкун",
    "зарох",
    "зарры",
    "землятян",
    "иичан",
    "инцель",
    "конатян",
    "кофесрач",
    "краутчан",
    "крипитян",
    "крисчан",
    "куклофаг",
    "лохотр",
    "луносрач",
    "луркмоар",
    "луркморе",
    "лурко",
    "луркоеб",
    "луркоебы",
    "луркой",
    "луркопаб",
    "луркофаг",
    "луркофак",
    "луркояз",
    "луркспик",
    "ляхосрач",
    "маскачан",
    "мемас",
    "мемасик",
    "мемасики",
    "мемез",
    "мемекоин",
    "мемтокен",
    "менточан",
    "монтян",
    "мочан",
    "мунтян",
    "мутить",
    "наукофаг",
    "нафиг",
    "нахер",
    "нацсрач",
    "нейро",
    "нейтон",
    "нехуй",
    "нульчат",
    "нульчер",
    "ньюсом",
    "нэймфаг",
    "нюфаг",
    "оверчан",
    "одинчан",
    "окточан",
    "остян",
    "очкочан",
    "пейнттян",
    "пиздят",
    "пиратчан",
    "поетред",
    "понифаги",
    "поничан",
    "пррчан",
    "путисрач",
    "путясрач",
    "пынясрач",
    "пыпасрач",
    "пыпесрач",
    "пэинттян",
    "ракочан",
    "рейты",
    "рефосрач",
    "ркнтян",
    "розенфаг",
    "рофел",
    "рулесрач",
    "славятян",
    "слюник",
    "смайлфаг",
    "срачи",
    "сссртян",
    "тегосрач",
    "турчан",
    "уберчан",
    "укросрач",
    "унылтян",
    "унылчан",
    "уродь",
    "фанон",
    "фотожаб",
    "фочан",
    "фурриарт",
    "фурричан",
    "хачан",
    "хохлочан",
    "хутисрач",
    "школочан",
    "эвосрач",
    "юваотян",
    "юлесрач",
    "юморек",
    "рилсы",
})

# Отклонения автора + множественные формы (не играем во мн.ч.).
COLLECT_REJECTED: frozenset[str] = USER_REJECTED | PLURAL_FORM_DENYLIST

# Ручной seed: двач, лурк, рунет, мемы, субкультуры (5–8 букв).
_MANUAL_RAW = """

бугурт битард ватник задрот олдфаг ньюфаг омежка форчан пдсрач нормис ламер 
доскач лентач ментач ньюсач нахрюк чайкун опкун кочан кункун ежчан бухтян модтян мэйтян
 чбтян модчан фурфаг макфаг крикун тиккун немем
мемчик чушпан киборд колчан ручан хачик нацик жирик поцик роглик соевик зэтник
зетник фашик пендос митник эмобой сойбой фембой томбой фейрик додик сквик чибик чятик
чатик чашик сычик аноним тролль паблик репост макрос гифка рунет пикабу реддит инвайт капча
донат вброс бекап макро набег маскот гоблач вебкам авито репорт спамер хикки хуита блогер
скамер ютубер твитер постер фейкер паста бампер ачивка дискач альфач куколд инцел
сигма деген аниме отаку кавай фурри вейпер фандом няшка тянка хакер вирус троян ботнет взлом
лулзы шизик петух скамер кринж богач богач лурка лурка срачик срачик
имба имба хайпан хайпан базар базар чадик чадик пикми пикми
омежка инцел инцел даунфаг нетфаг нетфаг геймер геймер стример стример
пикча пикча вебка вебка твича твича лампа лампа няшка кеклол кеклол
 попан тайпан фанфик фанфик тралик репчик рэпчик пездюк пиздюк пиздос
хуевик мандос педик пидор пидрил говнюк говняк мудак мудик мудло мразь
блядь блядка говно гнида дебил идиот козел кретин дурак тварь стерва падла
шлюха шмара херня хуйня фигня похер задрот задик задик лейбл лейбл
модель модель пиксель пиксель хостер хостер тредик тредик бордач бордач 
кибер кибер хакер крекер крекер малвар малвар руткит руткит фишинг фишинг
доксер доксер сватер сватер банхам банхам кикнут кикнут рейдж рейдж
неймфаг неймфаг копипаст шитпост анонимус выблядок имиджборд говносрач гомосрач
битард нульчан неймфага
абоба бумер зумер гойда гачик макак гринд крафт лутер модер нубик рашка сабка
скетч скилл скрин тильт челик чендж шортс иимем
амогус баффер билдер бустер вайбик двачер кекнут коллаб копиум крашик мемпик огонек
опчика прикол рандом рилсик рофлик рофлян селеба скиллз скрипт скуфик слопик соцфоб
телега тикток трапик упорот фармер фемцел форсер хайпер хейтер шиппер шитейк
шкурка юморок ядерка
баянист бибизян витубер гачимач геймдев геймпад гриндер дипфейк донатер кеквейт клиппер
крафтер кринжак кринжун лоликон лоликун лонгрид мемблог мемодел метовик ниточка озвучка
олдскул пепекун пепефаг пепечан плейбой подкаст пруфики реактор реакция рейпост
ролевик сасмейт смешняк спидран спойлер трапчик триггер тролинг фейспал форсинг
фотожоп хайлайт хардбас хардкор шейминг шкурник
геймплей импостер капибара клиповер кроспост летсплей луркомор метаверс нейроарт нейросет
пикабушн плейлист постирон скриншот тиктокер трукрайм фотожаба хайпмейк хайпожор хайпан
рунет троль вебкам лолчто мемчик репост спамер хиккач гейминг неймфаг нульчан
геймленд геймовер геймпасс булшит ватсап чатбот читкод шитман эмодзи эщкере говноед
""".split()

MANUAL_DVACH_SEED: frozenset[str] = frozenset(
    w for w in (normalize(x) for x in _MANUAL_RAW)
    if is_valid_shape(w, DVACH_LENGTHS)
)

# Бордословарь и «словарь двачера» (только подходящие по длине).
BOR_DICTIONARY: frozenset[str] = frozenset({
    w for w in {
        "бугурт", "битард", "ватник", "ачивка", "дискач", "вангую",
        "жирный",
    }
    if is_valid_shape(w, DVACH_LENGTHS)
} | {"ачивка", "дискач"})

# Имена персонажей / политиков / мусор из заголовков Неолурка.
TITLE_DENYLIST: frozenset[str] = frozenset({
    "степан", "патрик", "соник", "кратос", "кронос", "морфей", "портос", "яценюк", "данила",
    "микки", "пашка", "павлик", "егорик", "славик", "саник", "котик", "корлик", "клерик",
    "петрик", "сталик", "точик", "торик", "риддик", "лясик", "пухлик", "плюсик", "саэрос",
    "сасик", "живчик", "етник", "богиня", "звезды", "выборы", "адрес", "домен", "форум",
    "онлайн", "стрим", "френд", "вотсап", "скайп", "яндекс", "мамба", "агода", "анкета",
    "вкадре", "закреп", "спиреч", "рутвит", "фикбук", "птааг", "пукнум", "ибражы", "иносми",
    "арбуэ", "кравч", "кукуц", "лунач", "перняш", "пинач", "чухач", "вомбат", "аниас",
    "сапер", "хабра", "акунин", "якунин", "анатас", "брони", "вобля", "нигра",
    "джулуп", "диалап", "канобу", "микки", "пашка",
})

INTERNET_SLANG_SUFFIXES = ("фаг", "тян", "кун", "чан", "срач", "борд", "мем", "лурк", "тред", "пан")
INTERNET_MARKERS = (
    "двач", "лурк", "мем", "трол", "анон", "битар", "бугур", "ватник", "задрот", "пидор",
    "хуй", "бля", "говн", "пизд", "срач", "скуф", "омеж", "инцел", "фаг", "тян", "кун", "чан",
    "нейт", "рунет", "паблик", "репост", "гиф", "веб", "хик", "лол", "кек", "рофл", "бамп",
    "вайп", "скуф", "донат", "капч", "инвай", "спам", "трол", "форч", "имидж",
)

NEOLURK_INTERNET_CATS = {
    "Категория:Двач", "Категория:Имиджборды", "Категория:Интернет",
    "Категория:Сайты", "Категория:Рунет", "Категория:Форчансы",
}


def api(params: dict) -> dict:
    url = NEOLURK_API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def ensure_neolurk_titles() -> list[str]:
    cache = SOURCES / "neolurk_titles.txt"
    if cache.exists():
        return cache.read_text(encoding="utf-8").splitlines()

    titles: list[str] = []
    cont = None
    while True:
        params: dict = {"action": "query", "list": "allpages", "aplimit": "500", "apnamespace": "0"}
        if cont:
            params["apcontinue"] = cont
        data = api(params)
        titles.extend(p["title"] for p in data["query"]["allpages"])
        if "continue" not in data:
            break
        cont = data["continue"].get("apcontinue")
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text("\n".join(titles), encoding="utf-8")
    return titles


def is_strict_dvach_long_word(word: str) -> bool:
    """Жёсткий фильтр для 7–8 букв из Неолурка."""
    if word in NEOLURK_FALSE_POSITIVES:
        return False
    if word.endswith(("фаг", "фаги", "срач", "лурк", "борд", "чан", "кун", "тян", "тяны")):
        return True
    if word.startswith(
        ("двач", "лурк", "мем", "гейм", "говно", "анон", "битард", "задрот", "нульч", "неймф", "нэймф")
    ):
        return True
    if word in {
        "копипаст", "шитпост", "имиджборд", "имижборд", "анонимус", "выблядок", "биллборд",
    }:
        return True
    if any(
        word.startswith(p)
        for p in (
            "говносра", "гомосра", "богосра", "автосра", "жидосра", "игросра",
            "кофесра", "кописра", "ляхосра", "луносра", "нацсра", "наркосра",
        )
    ):
        return True
    return False


def single_word_from_title(title: str) -> str | None:
    if any(c in title for c in ' /:"()[]|'):
        return None
    word = normalize(title)
    if is_valid_shape(word, DVACH_LENGTHS):
        return word
    return None


def neolurk_search_words() -> set[str]:
    queries = [
        "двач", "имиджборд", "битард", "бугурт", "тред", "мем", "лурк", "форчан", "задрот",
        "олдфаг", "ньюфаг", "ватник", "омежка", "тролль", "срач", "вайп", "бамп", "рунет",
        "инцел", "куколд", "альфач", "шизик", "петросян", "лулз", "няша", "аниме", "отаку",
        "фурри", "вейпер", "паблик", "репост", "гифка", "хикки", "нормис", "ламер", "донат",
        "капча", "инвайт", "спамер", "скуф", "неймфаг", "аватар", "шитпост", "копипаста",
        "демотиватор", "пикабу", "реддит", "телеграм", "дискорд", "стример", "геймер",
    ]
    found: set[str] = set()
    for q in queries:
        data = api({"action": "query", "list": "search", "srsearch": q, "srlimit": "50"})
        for hit in data["query"]["search"]:
            w = single_word_from_title(hit["title"])
            if w:
                found.add(w)
        time.sleep(0.05)
    return found


def score_neolurk_word(word: str, morph: pymorphy2.MorphAnalyzer, harrix: set[str]) -> int:
    score = 0
    if any(word.endswith(s) for s in INTERNET_SLANG_SUFFIXES):
        score += 4
    if any(m in word for m in INTERNET_MARKERS):
        score += 3
    if word.startswith(("ней", "олд", "нью", "мега", "супер", "ультра")):
        score += 2
    parses = morph.parse(word)
    if not parses:
        return score + 2
    p = parses[0]
    tag = str(p.tag)
    if "UNKN" in tag:
        score += 3
    elif "Name" in tag:
        score += 1
    elif p.score < 0.35:
        score += 2
    elif "NOUN" in tag and p.score > 0.8 and word in harrix:
        score -= 4
    return score


def load_harrix_words() -> set[str]:
    path = SOURCES / "russian_nouns.txt"
    if not path.exists():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        w = normalize(line)
        if is_valid_shape(w, DVACH_LENGTHS):
            out.add(w)
    return out


def load_internet_titles(words: dict[str, str]) -> set[str]:
    cache = SOURCES / "neolurk_internet_words.txt"
    if cache.exists():
        return {normalize(w) for w in cache.read_text(encoding="utf-8").splitlines() if w.strip()}

    found: set[str] = set()
    items = list(words.items())
    for i in range(0, len(items), 50):
        batch_titles = [t for _, t in items[i : i + 50]]
        data = api({
            "action": "query",
            "titles": "|".join(batch_titles),
            "prop": "categories",
            "cllimit": "max",
        })
        for page in data["query"]["pages"].values():
            if page.get("missing"):
                continue
            w = normalize(page.get("title", ""))
            cats = {c["title"] for c in page.get("categories", [])}
            if cats & NEOLURK_INTERNET_CATS:
                found.add(w)
        time.sleep(0.08)
    cache.write_text("\n".join(sorted(found)), encoding="utf-8")
    return found


def collect() -> tuple[set[str], dict[str, str]]:
    morph = pymorphy2.MorphAnalyzer()
    harrix = load_harrix_words()

    titles = ensure_neolurk_titles()
    word_title: dict[str, str] = {}
    all_single: set[str] = set()
    for title in titles:
        w = single_word_from_title(title)
        if w:
            word_title[w] = title
            all_single.add(w)

    sources: dict[str, set[str]] = {
        "manual": set(MANUAL_DVACH_SEED),
        "bor": set(BOR_DICTIONARY),
        "search": neolurk_search_words(),
        "internet_cat": load_internet_titles(word_title),
    }

    scored: list[tuple[int, str]] = []
    for w in all_single:
        if w in TITLE_DENYLIST:
            continue
        if w in COLLECT_REJECTED:
            continue
        if len(w) >= 7 and not is_strict_dvach_long_word(w):
            continue
        s = score_neolurk_word(w, morph, harrix)
        if s >= 3:
            scored.append((s, w))
    scored.sort(reverse=True)
    sources["neolurk_scored"] = {w for _, w in scored}

    sources["suffix"] = {
        w for w in all_single
        if w not in TITLE_DENYLIST
        and w not in COLLECT_REJECTED
        and is_valid_shape(w, DVACH_LENGTHS)
        and (len(w) <= 6 or is_strict_dvach_long_word(w))
        and any(w.endswith(s) for s in INTERNET_SLANG_SUFFIXES)
    }

    merged: set[str] = set()
    origin: dict[str, str] = {}
    for name, words in sources.items():
        for w in words:
            if not is_valid_shape(w, DVACH_LENGTHS) or w in TITLE_DENYLIST or w in COLLECT_REJECTED:
                continue
            if len(w) >= 7 and name not in ("manual", "bor", "search") and not is_strict_dvach_long_word(w):
                continue
            merged.add(w)
            origin.setdefault(w, name)

    if len(merged) < MIN_DVACH_WORDS:
        for w in all_single:
            if w in TITLE_DENYLIST or w in COLLECT_REJECTED or w in merged:
                continue
            if len(w) >= 7 and not is_strict_dvach_long_word(w):
                continue
            if score_neolurk_word(w, morph, harrix) >= 2:
                merged.add(w)
                origin.setdefault(w, "neolurk_extra")
            if len(merged) >= MIN_DVACH_WORDS + 40:
                break

    deduped, dedup_reasons = deduplicate_dvach_words(merged, morph)
    deduped = {w for w in deduped if w not in COLLECT_REJECTED}
    for w, reason in dedup_reasons.items():
        origin[w] = f"removed:{reason}"

    return deduped, origin


def write_curated_data(words: set[str]) -> None:
    if len(words) < MIN_DVACH_WORDS:
        raise SystemExit(f"Собрано только {len(words)} слов, нужно минимум {MIN_DVACH_WORDS}")

    lines = sorted(words)
    body = ",\n".join(f"    {w!r}" for w in lines)
    content = f'''"""Словарь двача / рунета: мемы, имиджборды, интернет-лексика (5–8 букв).

Собран collect_dvach_words.py из:
- ручного seed (двач, лурк, бордословарь);
- заголовков статей Неолурка;
- поиска по Neolurk API.

Дедупликация: scripts/dictionary_dedup.py (множественное число, варианты написания).
Критерии: scripts/word_rules.py (passes_dvach_rules).
"""

from word_rules import passes_dvach_rules, reject_reason_dvach

MIN_DVACH_WORDS = {MIN_DVACH_WORDS}


def _validate_word(word: str) -> str:
    if not passes_dvach_rules(word):
        reason = reject_reason_dvach(word) or "не проходит правила"
        raise ValueError(f"{{word!r}}: {{reason}}")
    return word.strip().lower().replace("ё", "е")


CURATED_DVACH_NOUNS: frozenset[str] = frozenset({{
{body},
}})

for _w in CURATED_DVACH_NOUNS:
    _validate_word(_w)

_count5 = sum(1 for _w in CURATED_DVACH_NOUNS if len(_w.replace("ё", "е")) == 5)
_count6 = sum(1 for _w in CURATED_DVACH_NOUNS if len(_w.replace("ё", "е")) == 6)
_count7 = sum(1 for _w in CURATED_DVACH_NOUNS if len(_w.replace("ё", "е")) == 7)
_count8 = sum(1 for _w in CURATED_DVACH_NOUNS if len(_w.replace("ё", "е")) == 8)
_total = _count5 + _count6 + _count7 + _count8
if _total < MIN_DVACH_WORDS:
    raise ValueError(f"Мало слов двача: {{_total}}")
'''
    out = SCRIPTS / "dvach_curated_data.py"
    out.write_text(content, encoding="utf-8")


def main() -> None:
    words, origin = collect()
    write_curated_data(words)
    counts = {n: sum(1 for w in words if len(w) == n) for n in (5, 6, 7, 8)}
    print(f"Собрано {len(words)} слов ({counts[5]}/{counts[6]}/{counts[7]}/{counts[8]} по 5–8)")
    removed = [w for w, o in origin.items() if o.startswith("removed:")]
    if removed:
        print(f"  дедупликация убрала {len(removed)}: {', '.join(sorted(removed)[:12])}…")
    print(f"→ {SCRIPTS / 'dvach_curated_data.py'}")


if __name__ == "__main__":
    main()
