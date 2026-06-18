import type { WordLength } from "./daily";
import { toDisplay } from "./normalize";
import { loadWordBundle, type WordLexicon } from "./wordBundle";

const ANSWER_NORMAL_LENGTHS: WordLength[] = [5, 6];
const GUESS_EXTENDED_LENGTHS: WordLength[] = [7, 8];
const GUESS_PROFANITY_LENGTHS: WordLength[] = [5, 6];

async function loadDict(path: string): Promise<string[]> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`Не удалось загрузить словарь: ${path}`);
  }
  const text = await res.text();
  return text
    .split("\n")
    .map((line) => toDisplay(line.replace(/\r/g, "")))
    .filter(Boolean);
}

async function loadDictOptional(path: string): Promise<string[]> {
  try {
    return await loadDict(path);
  } catch {
    return [];
  }
}

export type LoadedDictionaries = {
  /** 5–6 букв: классическое слово дня + ввод. */
  normal: Partial<Record<WordLength, string[]>>;
  /** 7–8 букв: только ввод, не загадывается. */
  guessExtended: Partial<Record<WordLength, string[]>>;
  bundle: Partial<Record<WordLength, string[]>>;
  guessOnlyProfanity: Partial<Record<WordLength, string[]>>;
  lexicon: WordLexicon;
};

export async function loadDictionaries(): Promise<LoadedDictionaries> {
  const base = import.meta.env.BASE_URL;
  const lexicon = await loadWordBundle();

  const normal = {} as Partial<Record<WordLength, string[]>>;
  const guessExtended = {} as Partial<Record<WordLength, string[]>>;
  const guessOnlyProfanity = {} as Partial<Record<WordLength, string[]>>;

  await Promise.all([
    ...ANSWER_NORMAL_LENGTHS.map(async (len) => {
      normal[len] = await loadDict(`${base}dictionaries/ru-nouns-${len}.txt`);
    }),
    ...GUESS_EXTENDED_LENGTHS.map(async (len) => {
      guessExtended[len] = await loadDict(
        `${base}dictionaries/ru-guess-${len}.txt`,
      );
    }),
    ...GUESS_PROFANITY_LENGTHS.map(async (len) => {
      guessOnlyProfanity[len] = await loadDict(
        `${base}dictionaries/ru-profanity-nouns-${len}.txt`,
      );
    }),
  ]);

  const bundle = lexicon.byLength as Partial<Record<WordLength, string[]>>;

  return { normal, guessExtended, bundle, guessOnlyProfanity, lexicon };
}
