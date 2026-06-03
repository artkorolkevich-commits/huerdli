import type { WordLength } from "./daily";
import { toDisplay } from "./normalize";

async function loadDict(path: string): Promise<string[]> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`Не удалось загрузить словарь: ${path}`);
  }
  const text = await res.text();
  return text
    .split("\n")
    .map((line) => toDisplay(line))
    .filter(Boolean);
}

export type LoadedDictionaries = {
  normal: Record<WordLength, string[]>;
  profanity: Record<WordLength, string[]>;
};

export async function loadDictionaries(): Promise<LoadedDictionaries> {
  const lengths = [5, 6] as const;
  const normal = {} as Record<WordLength, string[]>;
  const profanity = {} as Record<WordLength, string[]>;

  await Promise.all(
    lengths.map(async (len) => {
      const base = import.meta.env.BASE_URL;
      const [n, p] = await Promise.all([
        loadDict(`${base}dictionaries/ru-nouns-${len}.txt`),
        loadDict(`${base}dictionaries/ru-profanity-nouns-${len}.txt`),
      ]);
      normal[len] = n;
      profanity[len] = p;
    }),
  );

  return { normal, profanity };
}
