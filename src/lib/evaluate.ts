export type LetterState = "correct" | "present" | "absent" | "empty";

export type EvaluatedLetter = {
  letter: string;
  state: LetterState;
};

/** Классическая логика Wordle с учётом повторов букв. */
export function evaluateGuess(guess: string, answer: string): EvaluatedLetter[] {
  const size = answer.length;
  const result: EvaluatedLetter[] = Array.from({ length: size }, (_, i) => ({
    letter: guess[i] ?? "",
    state: "absent" as LetterState,
  }));

  const answerCounts = new Map<string, number>();
  for (const ch of answer) {
    answerCounts.set(ch, (answerCounts.get(ch) ?? 0) + 1);
  }

  // Сначала зелёные
  for (let i = 0; i < size; i++) {
    if (guess[i] === answer[i]) {
      result[i] = { letter: guess[i]!, state: "correct" };
      answerCounts.set(guess[i]!, (answerCounts.get(guess[i]!) ?? 0) - 1);
    }
  }

  // Потом жёлтые
  for (let i = 0; i < size; i++) {
    if (result[i]!.state === "correct") continue;
    const ch = guess[i]!;
    const left = answerCounts.get(ch) ?? 0;
    if (left > 0) {
      result[i] = { letter: ch, state: "present" };
      answerCounts.set(ch, left - 1);
    } else {
      result[i] = { letter: ch, state: "absent" };
    }
  }

  return result;
}

export function mergeKeyboardState(
  current: Map<string, LetterState>,
  evaluated: EvaluatedLetter[],
): Map<string, LetterState> {
  const next = new Map(current);
  const rank: Record<LetterState, number> = {
    empty: 0,
    absent: 1,
    present: 2,
    correct: 3,
  };

  for (const { letter, state } of evaluated) {
    if (!letter) continue;
    const key = letter.toLowerCase();
    const prev = next.get(key);
    if (!prev || rank[state] > rank[prev]) {
      next.set(key, state);
    }
  }

  return next;
}
