/** Нормализация ввода: нижний регистр, Ё → Е, только кириллица. */
export function normalizeWord(raw: string): string {
  return raw
    .toLowerCase()
    .replace(/ё/g, "е")
    .replace(/[^а-я]/g, "");
}

export function toDisplay(raw: string): string {
  return normalizeWord(raw).toUpperCase();
}
