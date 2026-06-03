import { toDisplay } from "./normalize";

/** Сообщение при проигрыше: последняя попытка + «че серьёзно…» */
export function buildLoseMessage(lastGuess: string): string {
  const word = toDisplay(lastGuess) || "???";
  return `${word} ? че серьезно, поумней ничего не нашлось?`;
}
