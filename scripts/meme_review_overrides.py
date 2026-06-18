"""Ручные примеры и картинки для мемов без отдельной статьи на Неолурке."""

from __future__ import annotations

# word → enrichment (перекрывает автоматический сбор, если задано поле)
MEME_REVIEW_OVERRIDES: dict[str, dict[str, str]] = {
    "абоба": {
        "example": (
            "«Валерий Абоба — наш кандидат» — мем из ролика Глада Валакаса "
            "«Президент АБОБА» (2021): вымышленный кандидат в президенты, "
            "пародия на политические плакаты и шитпост в комментариях."
        ),
        "example_source": "https://lurkmore.org/wiki/%D0%93%D0%BB%D0%B0%D0%B4_%D0%92%D0%B0%D0%BB%D0%B0%D0%BA%D0%B0%D1%81",
        "example_title": "Глад Валакас",
        "image": "https://memepedia.ru/wp-content/uploads/2021/05/ftzbl5lkf1o.jpg",
        "image_source": "https://memepedia.ru/valerij-aboba-nash-kandidat-chto-za-fors/",
    },
    "бибизян": {
        "image": "https://neolurk.org/w/images/4/4b/Mshyg34.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9F%D1%80%D0%B8%D0%BA%D0%BE%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F_%D0%BE%D0%B1%D0%B5%D0%B7%D1%8C%D1%8F%D0%BD%D0%B0",
    },
    "хардбас": {
        "image": "https://neolurk.org/w/images/a/a5/Gop_vrubel.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%93%D0%BE%D0%BF%D0%BD%D0%B8%D0%BA",
    },
    "нетфаг": {
        "image": "https://neolurk.org/w/images/7/7c/Internet_Meme.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%98%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82",
    },
    "трукрайм": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/b/b6/True_Detective_magazine_cover_October_1961_issue.jpg",
        "image_source": "https://lurkmore.org/wiki/True_crime",
    },
    "шортс": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/YouTube_Shorts_player%2C_opened_on_a_video.png/440px-YouTube_Shorts_player%2C_opened_on_a_video.png",
        "image_source": "https://lurkmore.org/wiki/Shorts_(YouTube)",
    },
    "вейпер": {
        "image": "https://neolurk.org/w/images/c/cc/Colection.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%92%D0%B5%D0%B9%D0%BF",
    },
    "авито": {
        "image": "https://neolurk.org/w/images/8/84/Avito_logo1.png",
        "image_source": "https://lurkmore.org/wiki/%D0%90%D0%B2%D0%B8%D1%82%D0%BE",
    },
    "базар": {
        "image": "https://neolurk.org/w/images/9/9f/Md.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9E%D1%82%D0%B2%D0%B5%D1%87%D0%B0%D1%82%D1%8C_%D0%B7%D0%B0_%D0%B1%D0%B0%D0%B7%D0%B0%D1%80",
    },
    "боров": {
        "image": "https://neolurk.org/w/images/c/cf/Bebrock.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A7%D0%B5%D1%80%D0%B5%D0%BF%D0%B0%D1%88%D0%BA%D0%B8-%D0%BD%D0%B8%D0%BD%D0%B4%D0%B7%D1%8F",
    },
    "вайбик": {
        "image": "https://neolurk.org/w/images/a/a4/Yokoswimsuit.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9F%D0%BB%D1%8F%D0%B6",
    },
    "вангую": {
        "image": "https://neolurk.org/w/images/0/0d/Vanga.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%92%D0%B0%D0%BD%D0%B3%D0%B0",
    },
    "гандон": {
        "image": "https://neolurk.org/w/images/7/7f/Sert_condom.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%93%D0%BE%D0%BD%D0%B4%D0%BE%D0%BD",
    },
    "гондон": {
        "image": "https://neolurk.org/w/images/7/7f/Sert_condom.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%93%D0%BE%D0%BD%D0%B4%D0%BE%D0%BD",
    },
    "говновоз": {
        "image": "https://neolurk.org/w/images/4/49/Jkljkljkljjkljihjkl.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D0%B0%D0%B2%D0%B5%D1%80%D1%8B_%D1%81_%D0%B3%D0%BE%D0%B2%D0%BD%D0%BE%D0%B2%D0%BE%D0%B7%D0%BE%D0%BC",
    },
    "говнофон": {
        "image": "https://neolurk.org/w/images/0/06/Deita.jpg",
        "image_source": "https://lurkmore.org/wiki/Android",
    },
    "говнохуй": {
        "image": "https://neolurk.org/w/images/c/c1/Photo_202356658-18-04.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A7%D0%BB%D0%B5%D0%BD",
    },
    "гринд": {
        "image": "https://neolurk.org/w/images/9/92/World-of-warcraft-cover.jpg",
        "image_source": "https://lurkmore.org/wiki/World_of_Warcraft",
    },
    "деген": {
        "image": "https://neolurk.org/w/images/c/c4/GTASABOX.jpg",
        "image_source": "https://lurkmore.org/wiki/Grand_Theft_Auto:_San_Andreas",
    },
    "демка": {
        "image": "https://neolurk.org/w/images/f/f0/McCartney_vishivanka.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%92%D1%8B%D1%88%D0%B8%D0%B2%D0%B0%D0%BD%D0%BA%D0%B0_%D0%9C%D0%B0%D0%BA%D0%BA%D0%B0%D1%80%D1%82%D0%BD%D0%B8",
    },
    "дерьмо": {
        "image": "https://neolurk.org/w/images/a/a9/Motivator-govno2.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%93%D0%BE%D0%B2%D0%BD%D0%BE",
    },
    "дискач": {
        "image": "https://neolurk.org/w/images/c/cb/Schooldance.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A8%D0%BA%D0%BE%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5_%D1%82%D0%B0%D0%BD%D1%86%D1%8B",
    },
    "дискорд": {
        "image": "https://neolurk.org/w/images/a/a7/Discord_RAM.png",
        "image_source": "https://lurkmore.org/wiki/Discord",
    },
    "дойка": {
        "example": (
            "В сетевом сленге «дойка» — грубая сексуальная метафора; "
            "в мемах чаще встречается буквальная дойка коровы как абсурдная картинка."
        ),
        "example_source": "https://lurkmore.org/wiki/%D0%9A%D0%BE%D1%80%D0%BE%D0%B2%D0%B0",
        "example_title": "Корова",
        "image": "https://neolurk.org/w/images/5/51/%D0%97%D0%B2%D0%B5%D1%80%D1%83%D1%88%D0%BA%D0%B0.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D0%BE%D1%80%D0%BE%D0%B2%D0%B0",
    },
    "доксер": {
        "image": "https://neolurk.org/w/images/7/7f/Sert_condom.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%93%D0%BE%D0%BD%D0%B4%D0%BE%D0%BD",
    },
    "дупло": {
        "image": "https://neolurk.org/w/images/e/e6/403132_1.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%94%D1%83%D0%BF%D0%BB%D0%BE",
    },
    "ебало": {
        "image": "https://neolurk.org/w/images/e/e9/Zhirobas.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%96%D0%B8%D1%80%D0%BE%D0%B1%D0%B0%D1%81",
    },
    "жирдяй": {
        "image": "https://neolurk.org/w/images/e/e9/Zhirobas.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%96%D0%B8%D1%80%D0%BE%D0%B1%D0%B0%D1%81",
    },
    "коллаб": {
        "image": "https://neolurk.org/w/images/c/c5/Borba_gachi.jpg",
        "image_source": "https://lurkmore.org/wiki/Gachimuchi",
    },
    "крафт": {
        "image": "https://neolurk.org/w/images/1/13/Skyrim_gameplay.jpg",
        "image_source": "https://lurkmore.org/wiki/The_Elder_Scrolls_V:_Skyrim",
    },
    "крекер": {
        "image": "https://neolurk.org/w/images/4/4b/Cookies.jpg",
        "image_source": "https://lurkmore.org/wiki/Cookie",
    },
    "кроспост": {
        "image": "https://neolurk.org/w/images/c/c5/Borba_gachi.jpg",
        "image_source": "https://lurkmore.org/wiki/Gachimuchi",
    },
    "лонгрид": {
        "image": "https://neolurk.org/w/images/3/31/Longcat_long.jpg",
        "image_source": "https://lurkmore.org/wiki/Longcat",
    },
    "макак": {
        "image": "https://neolurk.org/w/images/b/b2/Sos.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B0%D0%BA%D0%B0%D0%BA%D0%B0",
    },
    "метаверс": {
        "image": "https://neolurk.org/w/images/e/ec/Crisis-in-infinite_spider-men.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A7%D0%B5%D0%BB%D0%BE%D0%B2%D0%B5%D0%BA-%D0%BF%D0%B0%D1%83%D0%BA",
    },
    "озвучка": {
        "image": "https://neolurk.org/w/images/1/10/Rubiks_cube.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D1%83%D0%B1%D0%B8%D0%BA-%D0%A0%D1%83%D0%B1%D0%B8%D0%BA",
    },
    "олень": {
        "image": "https://neolurk.org/w/images/c/cc/%D0%A5%D1%85_%D0%9E%D0%BB%D0%B5%D0%BD%D1%8C.JPG",
        "image_source": "https://lurkmore.org/wiki/%D0%9E%D0%BB%D0%B5%D0%BD%D1%8C",
    },
    "ослина": {
        "image": "https://neolurk.org/w/images/a/a5/Aaa036e4cb18e39c714f_XL.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9E%D1%81%D0%B5%D0%BB",
    },
    "пипка": {
        "image": "https://neolurk.org/w/images/c/c1/Photo_202356658-18-04.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9F%D0%B8%D1%81%D1%8E%D0%BD",
    },
    "подкаст": {
        "image": "https://neolurk.org/w/images/4/45/23575.png",
        "image_source": "https://lurkmore.org/wiki/%D0%9F%D0%BE%D0%B4%D0%BA%D0%B0%D1%81%D1%82",
    },
    "руткит": {
        "image": "https://neolurk.org/w/images/1/15/Minesweeperfail.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A1%D0%B0%D0%BF%D1%91%D1%80",
    },
    "сватер": {
        "image": "https://neolurk.org/w/images/0/08/Const5.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9E%D0%9C%D0%9E%D0%9D",
    },
    "селеба": {
        "image": "https://neolurk.org/w/images/f/ff/Zverey_net.JPG",
        "image_source": "https://lurkmore.org/wiki/%D0%A1%D0%B5%D1%80%D0%B3%D0%B5%D0%B9_%D0%97%D0%B2%D0%B5%D1%80%D0%B5%D0%B2",
    },
    "соцфоб": {
        "image": "https://neolurk.org/w/images/7/7f/Scream_Munch_orig.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D1%80%D0%B8%D0%BA",
    },
    "тянка": {
        "image": "https://neolurk.org/w/images/9/9a/Miku_hatsune.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A2%D1%8F%D0%BD",
    },
    "уебок": {
        "image": "https://neolurk.org/w/images/6/63/%D0%A4%D1%80%D0%B8%D1%82%D1%86%D0%BB%D1%8C.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%91%D0%BE%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9_%D1%83%D1%91%D0%B1%D0%BE%D0%BA",
    },
    "фагот": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/FoxBassoon.png/500px-FoxBassoon.png",
        "image_source": "https://ru.wikipedia.org/wiki/%D0%A4%D0%B0%D0%B3%D0%BE%D1%82",
    },
    "витубер": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Kizuna_AI_-_SCP_Foundation_2.png/440px-Kizuna_AI_-_SCP_Foundation_2.png",
        "image_source": "https://lurkmore.org/wiki/VTuber",
    },
    "хиккан": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Hikikomori%2C_Hiasuki%2C_2004.jpg/440px-Hikikomori%2C_Hiasuki%2C_2004.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A5%D0%B8%D0%BA%D0%B8%D0%BA%D0%BE%D0%BC%D0%BE%D1%80%D0%B8",
    },
    "хикка": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Hikikomori%2C_Hiasuki%2C_2004.jpg/440px-Hikikomori%2C_Hiasuki%2C_2004.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A5%D0%B8%D0%BA%D0%B8%D0%BA%D0%BE%D0%BC%D0%BE%D1%80%D0%B8",
    },
    "пикча": {
        "image": "https://neolurk.org/w/images/b/b4/Nordic-gamer-meme-1.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B0-%D1%80%D0%B5%D0%B0%D0%BA%D1%86%D0%B8%D1%8F",
    },
    "кеквейт": {
        "image": "https://neolurk.org/w/images/9/96/Pepe.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D0%B5%D0%BA",
    },
    "кеклол": {
        "image": "https://neolurk.org/w/images/9/96/Pepe.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D0%B5%D0%BA",
    },
    "кекнут": {
        "image": "https://neolurk.org/w/images/9/96/Pepe.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9A%D0%B5%D0%BA",
    },
    "мемблог": {
        "image": "https://neolurk.org/w/images/e/e7/MemeWork.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B5%D0%BC",
    },
    "мемпик": {
        "image": "https://neolurk.org/w/images/e/e7/MemeWork.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B5%D0%BC",
    },
    "мемск": {
        "image": "https://neolurk.org/w/images/e/e7/MemeWork.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B5%D0%BC",
    },
    "мемчик": {
        "image": "https://neolurk.org/w/images/e/e7/MemeWork.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B5%D0%BC",
    },
    "двачер": {
        "image": "https://neolurk.org/w/images/6/68/4chan_from_fishki_net.jpg",
        "image_source": "https://lurkmore.org/wiki/4chan",
    },
    "нейроарт": {
        "image": "https://neolurk.org/w/images/f/f8/C7v2v4575486pv1dvb1.webp",
        "image_source": "https://lurkmore.org/wiki/%D0%9D%D0%B5%D0%B9%D1%80%D0%BE%D1%81%D0%B5%D1%82%D0%B8",
    },
    "ядерка": {
        "image": "https://neolurk.org/w/images/c/c7/Photo_2022-06-28_22-00-55.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%AF%D0%B4%D0%B5%D1%80%D0%BD%D0%BE%D0%B5_%D0%BE%D1%80%D1%83%D0%B6%D0%B8%D0%B5",
    },
    "мемодел": {
        "image": "https://neolurk.org/w/images/e/e7/MemeWork.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B5%D0%BC",
    },
    "метовик": {
        "image": "https://neolurk.org/w/images/1/1e/2532.png",
        "image_source": "https://lurkmore.org/wiki/%D0%9C%D0%B5%D1%82%D0%B0%D0%B3%D0%B5%D0%B9%D0%BC%D0%B8%D0%BD%D0%B3",
    },
    "ниточка": {
        "image": "https://neolurk.org/w/images/4/41/Mainthreadrule.gif",
        "image_source": "https://lurkmore.org/wiki/%D0%A2%D1%80%D0%B5%D0%B4",
    },
    "шкурник": {
        "image": "https://neolurk.org/w/images/2/27/Guy_fawkes_mask_by_nacreouss-d462juf.png",
        "image_source": "https://lurkmore.org/wiki/%D0%A8%D0%BA%D1%83%D1%80%D0%B0",
    },
    "смешняк": {
        "image": "https://neolurk.org/w/images/a/ad/Rookie.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9D%D0%BE%D0%B2%D0%B8%D1%87%D0%BE%D0%BA",
    },
    "юморок": {
        "image": "https://neolurk.org/w/images/b/b4/Nordic-gamer-meme-1.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%AE%D0%BC%D0%BE%D1%80",
    },
    "сасмейт": {
        "image": "https://neolurk.org/w/images/a/a9/Motivator-govno2.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%A1%D0%B0%D1%81",
    },
    "нубик": {
        "image": "https://neolurk.org/w/images/a/ad/Rookie.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%9D%D0%BE%D0%B2%D0%B8%D1%87%D0%BE%D0%BA",
    },
    "говноед": {
        "image": "https://neolurk.org/w/images/a/a9/Motivator-govno2.jpg",
        "image_source": "https://lurkmore.org/wiki/%D0%93%D0%BE%D0%B2%D0%BD%D0%BE",
    },
    "крашик": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Heart_coraz%C3%B3n.svg/440px-Heart_coraz%C3%B3n.svg.png",
        "image_source": "https://ru.wikipedia.org/wiki/%D0%9A%D1%80%D0%B0%D1%88",
    },
    "клиппер": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/YouTube_Shorts_player%2C_opened_on_a_video.png/440px-YouTube_Shorts_player%2C_opened_on_a_video.png",
        "image_source": "https://lurkmore.org/wiki/YouTube",
    },
    "клиповер": {
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/YouTube_Shorts_player%2C_opened_on_a_video.png/440px-YouTube_Shorts_player%2C_opened_on_a_video.png",
        "image_source": "https://lurkmore.org/wiki/YouTube",
    },
}

# Сленг → каноническая статья Неолурка (если у слова нет своей иллюстрации).
MEME_NEOLURK_TITLE_MAP: dict[str, str] = {
    "амогус": "Among Us",
    "импостер": "Among Us",
    "гачик": "Gachimuchi",
    "гачимач": "Gachimuchi",
    "кринжак": "Кринж",
    "кринжун": "Кринж",
    "даунфаг": "Даун",
    "постирон": "Постирония",
    "рилсик": "Instagram",
    "иимем": "Нейросети",
    "нейросет": "Нейросети",
    "лоликун": "Lolicon",
    "лоликон": "Lolicon",
    "опчика": "Оп",
    "неолурк": "Неолурк",
    "луркомор": "Луркоморье",
    "скуфик": "Скуф",
    "мемпик": "Мем",
    "мемчик": "Мем",
    "мемблог": "Мем",
    "мемск": "Мем",
    "пикабушн": "Пикабу",
    "фейспал": "Facepalm",
    "шитейк": "Шитпост",
    "шитман": "Шитпост",
    "фигня": "Фигня, переделывай",
    "гойда": "Гойда",
    "дипфейк": "Дипфейк",
    "ботнет": "Ботнет",
    "витубер": "VTuber",
    "хиккан": "Хикикомори",
    "хикка": "Хикикомори",
    "эщкере": "Эщкере",
    "хардбас": "Hardbass",
    "метаверс": "Метавселенная",
    "нетфаг": "Нетфаг",
    "кеквейт": "Кек",
    "кеклол": "Кек",
    "кекнут": "Кек",
    "трукрайм": "True crime",
    "булшит": "Буллшит",
    "лолчто": "LOL",
    "викимем": "Викимем",
    "рофлик": "ROFL",
    "рофлян": "ROFL",
    "трапик": "Трап",
    "трапчик": "Трап",
    "пепефаг": "Лягушонок Пепе",
    "пепекун": "Лягушонок Пепе",
    "пепечан": "Лягушонок Пепе",
    "хайпан": "Хайп",
    "хайпмейк": "Хайп",
    "хайпожор": "Хайп",
    "хайпер": "Хайп",
    "вейпер": "Вейпер",
    "рейпост": "Репост",
    "срачик": "Срач",
    "пикча": "Картинка-реакция",
    "мемодел": "Мем",
    "нейроарт": "Нейросети",
    "ядерка": "Ядерное оружие",
    "селеба": "Селебрити",
    "соцфоб": "Социофобия",
    "сабка": "Сабреддит",
    "смешняк": "Смех",
    "юморок": "Юмор",
    "шкурник": "Шкур",
    "сасмейт": "Сас",
    "метовик": "Мета",
    "ниточка": "Нитка",
    "челик": "Чел",
    "шортс": "Shorts (YouTube)",
    "двачер": "Двач",
}

# Если прямой заголовок не найден — ищем по связанной статье.
MEME_RELATED_NEOLURK_SEARCH: dict[str, str] = {
    "абоба": "Глад Валакас",
}
