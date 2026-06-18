# Хуердли

Русская Wordle-игра: слово дня **одинаково у всех игроков** (дата по **Europe/Moscow**).

## Запуск

```bash
npm install
npm run dev
```

Откройте http://localhost:5173

## Правила (прототип)

- **5 или 6 букв** (случайно каждый день, одинаково у всех), 6 попыток
- Пн / Ср / Пт — слово из матового словаря (18+)
- Остальные дни — обычный словарь
- Ё приводится к Е
- Прогресс сохраняется в `localStorage` на устройстве

## Одинаковое слово для всех

Алгоритм в `src/lib/daily.ts`:

1. `dateKey` = календарный день в часовом поясе **Москвы**
2. Длина = `5 + hash(dateKey + ':len') % 2` → 5 или 6 букв
3. Матовый день = понедельник, среда, пятница (по Москве)
4. Индекс слова = `floor(rng(hash(dateKey + ':word:…')) * len(dict))`

Один и тот же код + та же дата → одно слово на телефоне, ноуте и у друга.

Проверка в консоли браузера: `window.__HUERDLI__.puzzle`

## Словари

Игра использует словари для 5 и 6 букв:

- `ru-nouns-{5,6}.txt`
- `ru-profanity-nouns-{5,6}.txt` — матовые дни (Пн / Ср / Пт), только кириллица
- `ru-dvach-nouns-{5,6}.txt` — словарь двача / рунета (**307 слов**, 147 + 160)

### Правила отбора слов

Каждое слово должно быть **реальной единицей русской лексики** с понятным
смыслом — его можно объяснить, даже если оно редкое или грубое. Мат и
нейтральная лексика проходят одни и те же критерии качества.

Полный текст правил: [`scripts/word_rules.py`](scripts/word_rules.py)
(константа `DICTIONARY_RULES`).

Кратко:

- только кириллица, 5–6 букв (Ё → Е);
- существительное, не обрывок и не имя собственное;
- обычный словарь: Harrix/Russian-Nouns + морфологический фильтр;
- матовый словарь: ручной curated-список без обрезанных форм
  (`долбо`, `подон`, `шалав` и т.п.);
- двач-словарь: Неолурк + бордословарь + ручной seed, см. ниже.

Матовый список редактируется в `scripts/profanity_curated_data.py`, затем:

```bash
.venv/bin/python scripts/build_dictionaries.py
npm run dict:sync
```

### Словарь двача (`ru-dvach-nouns-*.txt`)

Собирается скриптом `scripts/collect_dvach_words.py` из:

- заголовков статей [Неолурка](https://lurkmore.org/) (мемы, имиджборды, рунет);
- поиска по Neolurk API;
- ручного seed (двачевский сленг, бордословарь, интернет-лексика).

Минимум **300** слов (5 + 6 букв). Пересборка:

```bash
.venv/bin/python scripts/collect_dvach_words.py   # обновить dvach_curated_data.py
.venv/bin/python scripts/build_dictionaries.py
npm run dict:sync
```

Список хранится в `scripts/dvach_curated_data.py`.

## Сборка

```bash
npm run build
npm run preview
```

## Деплой на GitHub Pages

GitHub достаточно: игра статическая, сервер не нужен. Один и тот же URL → одно слово дня у всех.

### 1. Репозиторий на GitHub

1. [github.com/new](https://github.com/new) → имя, например `huerdli` (латиница, без пробелов)
2. Репозиторий **Public** (Pages бесплатно только для public)

### 2. Залить код

```bash
cd "/Users/artkorol/.cursor/plans/Хуердли"
git init
git add .
git commit -m "Initial commit: Хуердли"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/huerdli.git
git push -u origin main
```

### 3. Включить Pages

В репозитории: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

После push в `main` workflow `.github/workflows/deploy.yml` соберёт проект и опубликует `dist/`.

### 4. Ссылка для друзей

```
https://ВАШ_ЛОГИН.github.io/huerdli/
```

Имя в URL = имя репозитория. Словари и алгоритм слова дня одинаковые у всех, кто открыл эту ссылку.

### Локальная проверка «как на Pages»

```bash
VITE_BASE_PATH=/huerdli/ npm run build
npx vite preview --base /huerdli/
```

### Если репозиторий называется `username.github.io`

Для личного сайта в корне домена в workflow замените `VITE_BASE_PATH` на `/` (см. комментарий в `deploy.yml`).
