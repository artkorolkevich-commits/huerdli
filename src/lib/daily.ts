import { getGameNumber } from "./stats";

export type WordLength = 5 | 6;

/** FNV-1a — одинаковый результат во всех JS-движках. */
export function hashString(input: string): number {
  let hash = 2166136261;
  for (let i = 0; i < input.length; i++) {
    hash ^= input.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function mulberry32(seed: number): () => number {
  let state = seed;
  return () => {
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), state | 1);
    t = (t + Math.imul(t ^ (t >>> 7), t | 61)) | 0;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Календарная дата по Москве — у всех игроков один и тот же «день». */
export function getMoscowDateKey(now = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Moscow",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now);
}

/** Пн, Ср, Пт — матовые дни. */
export function isProfanityDay(now = new Date()): boolean {
  const weekday = new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Moscow",
    weekday: "short",
  }).format(now);

  return weekday === "Mon" || weekday === "Wed" || weekday === "Fri";
}

/** Разовые замены слова дня (дата Москвы → слово). Удалить после использования. */
const DAILY_WORD_OVERRIDES: Record<string, string> = {
  "2026-06-03": "бляшка",
};

export function pickWordLength(dateKey: string): WordLength {
  return (5 + (hashString(`${dateKey}:len`) % 2)) as WordLength;
}

export type DailyPuzzle = {
  dateKey: string;
  gameNumber: number;
  length: WordLength;
  profanity: boolean;
  word: string;
  index: number;
};

export type WordPools = Record<
  WordLength,
  { normal: string[]; profanity: string[]; guess: Set<string> }
>;

export function buildWordPools(
  normal: Record<WordLength, string[]>,
  profanity: Record<WordLength, string[]>,
): WordPools {
  const pools = {} as WordPools;
  for (const len of [5, 6] as const) {
    pools[len] = {
      normal: normal[len],
      profanity: profanity[len],
      guess: new Set([...normal[len], ...profanity[len]]),
    };
  }
  return pools;
}

export function pickDailyWord(
  dateKey: string,
  profanity: boolean,
  pools: WordPools,
): DailyPuzzle {
  const length = pickWordLength(dateKey);
  const words = profanity ? pools[length].profanity : pools[length].normal;

  if (words.length === 0) {
    throw new Error(`Пустой словарь для длины ${length}`);
  }

  const overrideRaw = DAILY_WORD_OVERRIDES[dateKey];
  if (overrideRaw) {
    const normalized = overrideRaw.toLowerCase().replace(/ё/g, "е");
    const match = words.find((w) => w.toLowerCase().replace(/ё/g, "е") === normalized);
    if (match && match.length === length) {
      return {
        dateKey,
        gameNumber: getGameNumber(dateKey),
        length,
        profanity,
        word: match,
        index: words.indexOf(match),
      };
    }
  }

  const rng = mulberry32(
    hashString(`${dateKey}:word:${length}:${profanity ? "p" : "n"}`),
  );
  const index = Math.floor(rng() * words.length);

  return {
    dateKey,
    gameNumber: getGameNumber(dateKey),
    length,
    profanity,
    word: words[index]!,
    index,
  };
}
