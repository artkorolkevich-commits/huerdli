import type { DailyPuzzle } from "./daily";
import { evaluateGuess, type LetterState } from "./evaluate";

const EMOJI: Record<LetterState, string> = {
  correct: "🟩",
  present: "🟨",
  absent: "⬛",
  empty: "⬜",
};

function formatDateShort(dateKey: string): string {
  const [y, m, d] = dateKey.split("-").map(Number);
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "Europe/Moscow",
  }).format(new Date(Date.UTC(y!, m! - 1, d!)));
}

export function buildShareGrid(guesses: string[], answer: string): string {
  return guesses
    .map((guess) =>
      evaluateGuess(guess, answer)
        .map(({ state }) => EMOJI[state])
        .join(""),
    )
    .join("\n");
}

export function buildShareText(
  puzzle: DailyPuzzle,
  guesses: string[],
  status: "won" | "lost",
  gameUrl: string,
): string {
  const attempts = status === "won" ? `${guesses.length}/6` : "X/6";

  const lines = [
    `Хуердли ${formatDateShort(puzzle.dateKey)} · ${puzzle.length} букв`,
    attempts,
    "",
    buildShareGrid(guesses, puzzle.word),
    "",
    gameUrl,
  ];

  return lines.join("\n");
}

export function getGameUrl(): string {
  const base = import.meta.env.BASE_URL;
  const path = base.endsWith("/") ? base : `${base}/`;
  return `${window.location.origin}${path}`;
}

export function buildTelegramShareUrl(shareText: string): string {
  return `https://t.me/share/url?text=${encodeURIComponent(shareText)}`;
}

export async function copyShareText(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}
