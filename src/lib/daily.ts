import { GAME_EPOCH, getGameNumber } from "./stats";
import { toDisplay } from "./normalize";

export type WordLength = 5 | 6 | 7 | 8;

const WORD_LENGTHS: WordLength[] = [5, 6, 7, 8];
const CLASSIC_LENGTHS: WordLength[] = [5, 6];
const MEME_LENGTHS: WordLength[] = [5, 6, 7, 8];

/** Меняем при смене алгоритма ротации — пересчёт слов дня. */
export const WORD_SCHEDULE_VERSION = "v4";

const WEEKDAY_INDEX: Record<string, number> = {
  Mon: 0,
  Tue: 1,
  Wed: 2,
  Thu: 3,
  Fri: 4,
  Sat: 5,
  Sun: 6,
};

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

function parseDateKey(dateKey: string): number {
  const [y, m, d] = dateKey.split("-").map(Number);
  return Date.UTC(y!, m! - 1, d!);
}

function nextDateKey(dateKey: string): string {
  const ms = parseDateKey(dateKey) + 86_400_000;
  const d = new Date(ms);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
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

function getMoscowWeekdayShort(dateKey: string): string {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Moscow",
    weekday: "short",
  }).format(new Date(parseDateKey(dateKey)));
}

/** Недели с GAME_EPOCH — для ротации «классического» дня недели. */
function getWeeksSinceEpoch(dateKey: string): number {
  const diff = Math.round(
    (parseDateKey(dateKey) - parseDateKey(GAME_EPOCH)) / 86_400_000,
  );
  return Math.floor(diff / 7);
}

/** 0 = пн, 1 = вт, … — какой день недели «классический» на этой неделе. */
export function getClassicWeekdayIndex(dateKey: string): number {
  return ((getWeeksSinceEpoch(dateKey) % 7) + 7) % 7;
}

/** Раз в неделю — слово из обычного словаря Harrix. */
export function isClassicDay(dateKey: string): boolean {
  const weekday = getMoscowWeekdayShort(dateKey);
  const idx = WEEKDAY_INDEX[weekday];
  return idx !== undefined && idx === getClassicWeekdayIndex(dateKey);
}

/** @deprecated Используйте isClassicDay — оставлено для совместимости отладки. */
export function isProfanityDay(now = new Date()): boolean {
  return !isClassicDay(getMoscowDateKey(now));
}

/** Разовые замены слова дня (дата Москвы → слово). */
const DAILY_WORD_OVERRIDES: Record<string, string> = {
  "2026-06-03": "пердун",
};

export type DailyPuzzle = {
  dateKey: string;
  gameNumber: number;
  length: WordLength;
  /** true = обычный словарь Harrix, false = игровой бандл (мемы/двач/мат). */
  classic: boolean;
  /** @deprecated Используйте classic. */
  profanity: boolean;
  word: string;
  index: number;
};

export type LengthPool = {
  /** Слова для отгадывания в «классический» день. */
  normalAnswer: string[];
  /** Слова для отгадывания в дни бандла. */
  bundleAnswer: string[];
  /** Все слова, которые можно вводить. */
  guess: Set<string>;
  shuffledNormal: string[];
  shuffledBundle: string[];
};

export type WordPools = Record<WordLength, LengthPool>;

function shuffleWords(words: string[], seedKey: string): string[] {
  const arr = [...words];
  const rng = mulberry32(
    hashString(`${WORD_SCHEDULE_VERSION}:${seedKey}`),
  );
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j]!, arr[i]!];
  }
  return arr;
}

export function buildWordPools(
  normal: Partial<Record<WordLength, string[]>>,
  bundle: Partial<Record<WordLength, string[]>>,
  guessOnlyProfanity: Partial<Record<WordLength, string[]>>,
  guessExtended: Partial<Record<WordLength, string[]>>,
): WordPools {
  const pools = {} as WordPools;

  for (const len of WORD_LENGTHS) {
    const normalAnswer =
      len === 5 || len === 6 ? (normal[len] ?? []) : [];
    const bundleAnswer = bundle[len] ?? [];
    const profanityGuess = guessOnlyProfanity[len] ?? [];
    const extendedGuess = guessExtended[len] ?? [];

    const guess = new Set<string>([
      ...normalAnswer,
      ...bundleAnswer,
      ...profanityGuess,
      ...extendedGuess,
    ]);

    pools[len] = {
      normalAnswer,
      bundleAnswer,
      guess,
      shuffledNormal: shuffleWords(normalAnswer, `normal:${len}`),
      shuffledBundle: shuffleWords(bundleAnswer, `bundle:${len}`),
    };
  }

  return pools;
}

function availableLengths(
  classic: boolean,
  pools: WordPools,
): WordLength[] {
  const candidates = classic ? CLASSIC_LENGTHS : MEME_LENGTHS;
  return candidates.filter((len) => {
    const pool = classic
      ? pools[len].normalAnswer
      : pools[len].bundleAnswer;
    return pool.length > 0;
  });
}

export function pickWordLength(
  dateKey: string,
  classic: boolean,
  pools: WordPools,
): WordLength {
  const lengths = availableLengths(classic, pools);
  if (lengths.length === 0) {
    throw new Error(
      classic
        ? "Пустой классический словарь"
        : "Пустой словарь бандла",
    );
  }
  const idx = hashString(`${dateKey}:len`) % lengths.length;
  return lengths[idx]!;
}

function poolSlotIndex(
  dateKey: string,
  classic: boolean,
  length: WordLength,
  pools: WordPools,
): number {
  let slot = 0;
  let d = GAME_EPOCH;
  while (d < dateKey) {
    const dayClassic = isClassicDay(d);
    const dayLength = pickWordLength(d, dayClassic, pools);
    if (dayClassic === classic && dayLength === length) {
      slot += 1;
    }
    d = nextDateKey(d);
  }
  return slot;
}

function pickFromShuffledPool(
  shuffled: string[],
  slot: number,
): { word: string; index: number } {
  if (shuffled.length === 0) {
    throw new Error("Пустой пул слов");
  }
  const index = slot % shuffled.length;
  return { word: shuffled[index]!, index };
}

export function pickDailyWord(
  dateKey: string,
  pools: WordPools,
): DailyPuzzle {
  const classic = isClassicDay(dateKey);
  const length = pickWordLength(dateKey, classic, pools);
  const answerPool = classic
    ? pools[length].shuffledNormal
    : pools[length].shuffledBundle;

  const overrideRaw = DAILY_WORD_OVERRIDES[dateKey];
  if (overrideRaw) {
    const normalized = toDisplay(overrideRaw);
    const match = answerPool.find((w) => w === normalized);
    if (match) {
      return {
        dateKey,
        gameNumber: getGameNumber(dateKey),
        length,
        classic,
        profanity: !classic,
        word: match,
        index: answerPool.indexOf(match),
      };
    }
  }

  const slot = poolSlotIndex(dateKey, classic, length, pools);
  const shuffled = classic
    ? pools[length].shuffledNormal
    : pools[length].shuffledBundle;
  const { word, index } = pickFromShuffledPool(shuffled, slot);

  return {
    dateKey,
    gameNumber: getGameNumber(dateKey),
    length,
    classic,
    profanity: !classic,
    word,
    index,
  };
}
