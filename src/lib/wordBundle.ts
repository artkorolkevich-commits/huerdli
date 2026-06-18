import { toDisplay } from "./normalize";

export type WordBundleEntry = {
  word: string;
  length: number;
  sources: string[];
  definition: string;
  example?: string | null;
  example_source?: string | null;
  example_title?: string | null;
  image?: string | null;
  image_source?: string | null;
};

export type WordBundle = {
  version: number;
  words: WordBundleEntry[];
};

export type WordLexicon = {
  byWord: Map<string, WordBundleEntry>;
  byLength: Record<number, string[]>;
};

export async function loadWordBundle(): Promise<WordLexicon> {
  const base = import.meta.env.BASE_URL;
  const res = await fetch(`${base}dictionary-bundle.json`);
  if (!res.ok) {
    throw new Error("Не удалось загрузить dictionary-bundle.json");
  }
  const bundle = (await res.json()) as WordBundle;
  const byWord = new Map<string, WordBundleEntry>();
  const byLength: Record<number, string[]> = { 5: [], 6: [], 7: [], 8: [] };

  for (const entry of bundle.words) {
    const word = toDisplay(entry.word);
    byWord.set(word, { ...entry, word });
    const len = entry.length;
    if (len >= 5 && len <= 8) {
      byLength[len]!.push(word);
    }
  }

  return { byWord, byLength };
}

export function getWordEntry(
  lexicon: WordLexicon,
  word: string,
): WordBundleEntry | undefined {
  return lexicon.byWord.get(toDisplay(word));
}
