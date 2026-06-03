import { toDisplay } from "./normalize";

const LOSE_MESSAGES_STATIC = [
  "Ты лошара потный",
  "Ну ты чмо",
  "Ну ты и даун",
  "Ну ты тупица",
  "Ты тупой чтоли?",
  "Ну ты даёшь, конечно",
  "Что, поумней вариантов не смог придумать?",
  "Лох",
  "Пффф, иди вообще отсюда",
  "Game over, а кто вообще сомневался?",
  "В другой день попробуешь поумничать",
  "Как вообще можно было не отгадать?",
  "Ебаа.. так просто ведь было",
  "Не получилось? Лошара",
  "В следующий раз башку включай",
  "Иди молочка попей, успокойся",
  "Сорри конечно, но это было тупо",
  "Давай уже, кончай тупить, завтра отгадывать приходи",
  "Ну так день начинать конечно не надо",
] as const;

/** Вариант с последней (6-й) попыткой: «ЗАЛУПА ? че серьезно…» */
export function buildLoseMessageWithLastGuess(lastGuess: string): string {
  const word = toDisplay(lastGuess) || "???";
  return `${word} ? че серьезно, поумней ничего не нашлось?`;
}

/** Одна случайная фраза для окна результата (в т.ч. с последним словом). */
export function pickLoseMessage(lastGuess: string): string {
  const pool = [...LOSE_MESSAGES_STATIC, buildLoseMessageWithLastGuess(lastGuess)];
  const index = Math.floor(Math.random() * pool.length);
  return pool[index]!;
}
