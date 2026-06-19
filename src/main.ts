import {
  buildWordPools,
  getMoscowDateKey,
  isClassicDay,
  pickDailyWord,
  type DailyPuzzle,
  type WordPools,
} from "./lib/daily";
import { loadDictionaries } from "./lib/dictionaries";
import {
  evaluateGuess,
  mergeKeyboardState,
  type EvaluatedLetter,
  type LetterState,
} from "./lib/evaluate";
import { toDisplay } from "./lib/normalize";
import { pickLoseMessage } from "./lib/loseMessages";
import { pickWinMessage } from "./lib/winMessages";
import { buildShareGrid, buildShareText, copyShareText, getGameUrl } from "./lib/share";
import {
  isStatsRecorded,
  loadStats,
  maxDistribution,
  recordGameResult,
  winRate,
} from "./lib/stats";
import { getWordEntry, type WordLexicon } from "./lib/wordBundle";
import "./style.css";

const MAX_GUESSES = 6;
const ADULT_KEY = "huerdli-adult-v1";

const KEYBOARD_ROWS = [
  ["й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ"],
  ["ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э"],
  ["backspace", "я", "ч", "с", "м", "и", "т", "ь", "б", "ю", "enter"],
];

type SavedState = {
  dateKey: string;
  length: number;
  guesses: string[];
  status: "playing" | "won" | "lost";
  loseMessage?: string;
  winMessage?: string;
};

type GameContext = {
  puzzle: DailyPuzzle;
  pools: WordPools;
  lexicon: WordLexicon;
  guesses: string[];
  current: string;
  status: "playing" | "won" | "lost";
  keyboard: Map<string, LetterState>;
  loseMessage: string | null;
  winMessage: string | null;
};

const boardEl = document.getElementById("board")!;
const keyboardEl = document.getElementById("keyboard")!;
const messageEl = document.getElementById("message")!;
const subtitleEl = document.getElementById("subtitle")!;
const modalEl = document.getElementById("modal")!;
const modalTitleEl = document.getElementById("modal-title")!;
const modalTextEl = document.getElementById("modal-text")!;
const modalBtnEl = document.getElementById("modal-btn")!;
const modalShareEl = document.getElementById("modal-share") as HTMLButtonElement;
const modalShareBlockEl = document.getElementById("modal-share-block")!;
const modalSharePreviewEl = document.getElementById("modal-share-preview")!;
const modalShareLinkEl = document.getElementById("modal-share-link") as HTMLAnchorElement;
const modalAnswerRowEl = document.getElementById("modal-answer-row")!;
const modalAnswerWordEl = document.getElementById("modal-answer-word")!;
const modalExplainerBtnEl = document.getElementById("modal-explainer-btn")!;
const modalExplainerEl = document.getElementById("modal-explainer")!;
const modalExplainerDefinitionEl = document.getElementById("modal-explainer-definition")!;
const modalExplainerExampleEl = document.getElementById("modal-explainer-example")!;
const modalExplainerFigureEl = document.getElementById("modal-explainer-figure")!;
const modalExplainerImageEl = document.getElementById("modal-explainer-image") as HTMLImageElement;
const shareBtnEl = document.getElementById("share-btn") as HTMLButtonElement;
const statsBtnEl = document.getElementById("stats-btn") as HTMLButtonElement;
const statsModalEl = document.getElementById("stats-modal")!;
const statsBodyEl = document.getElementById("stats-body")!;
const statsCloseEl = document.getElementById("stats-close") as HTMLButtonElement;
const ageGateEl = document.getElementById("age-gate")!;
const ageYesEl = document.getElementById("age-yes")!;
const ageNoEl = document.getElementById("age-no")!;

let game: GameContext;
/** Строка с анимацией переворота после отправки слова; null — без анимации. */
let revealingRow: number | null = null;

/** Меняем при смене слова дня — старые сохранения игнорируются. */
const GAME_STORAGE_VERSION = 4;

function storageKey(dateKey: string): string {
  return `huerdli-game-v${GAME_STORAGE_VERSION}-${dateKey}`;
}

function loadSaved(dateKey: string, length: number): SavedState | null {
  try {
    const raw = localStorage.getItem(storageKey(dateKey));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as SavedState;
    if (parsed.dateKey !== dateKey || parsed.length !== length) return null;
    return parsed;
  } catch {
    return null;
  }
}

function saveGame(): void {
  const payload: SavedState = {
    dateKey: game.puzzle.dateKey,
    length: game.puzzle.length,
    guesses: game.guesses,
    status: game.status,
    ...(game.status === "lost" && game.loseMessage
      ? { loseMessage: game.loseMessage }
      : {}),
    ...(game.status === "won" && game.winMessage
      ? { winMessage: game.winMessage }
      : {}),
  };
  localStorage.setItem(storageKey(game.puzzle.dateKey), JSON.stringify(payload));
}

function isAdultConfirmed(): boolean {
  return localStorage.getItem(ADULT_KEY) === "true";
}

function setMessage(text: string, kind: "info" | "error" | "success" = "info"): void {
  messageEl.textContent = text;
  messageEl.dataset.kind = kind;
}

function showModal(title: string, text: string): void {
  modalTitleEl.textContent = title;
  modalTextEl.textContent = text;
  modalShareBlockEl.classList.add("hidden");
  modalAnswerRowEl.classList.add("hidden");
  collapseWordExplainer();
  modalEl.classList.remove("hidden");
}

function hideModal(): void {
  modalEl.classList.add("hidden");
  collapseWordExplainer();
}

function collapseWordExplainer(): void {
  modalExplainerEl.classList.add("hidden");
  modalExplainerBtnEl.setAttribute("aria-expanded", "false");
}

function renderWordExplainer(word: string): void {
  const entry = getWordEntry(game.lexicon, word);
  if (!entry) {
    modalExplainerDefinitionEl.textContent = "Краткого объяснения пока нет.";
    modalExplainerExampleEl.textContent = "";
    modalExplainerExampleEl.classList.add("hidden");
    modalExplainerFigureEl.classList.add("hidden");
    return;
  }

  modalExplainerDefinitionEl.textContent = entry.definition;

  if (entry.example) {
    modalExplainerExampleEl.textContent = entry.example;
    modalExplainerExampleEl.classList.remove("hidden");
  } else {
    modalExplainerExampleEl.textContent = "";
    modalExplainerExampleEl.classList.add("hidden");
  }

  if (entry.image) {
    modalExplainerImageEl.src = entry.image;
    modalExplainerImageEl.alt = entry.word;
    modalExplainerFigureEl.classList.remove("hidden");
  } else {
    modalExplainerImageEl.removeAttribute("src");
    modalExplainerFigureEl.classList.add("hidden");
  }
}

function toggleWordExplainer(): void {
  const expanded = !modalExplainerEl.classList.contains("hidden");
  if (expanded) {
    collapseWordExplainer();
    return;
  }
  renderWordExplainer(game.puzzle.word);
  modalExplainerEl.classList.remove("hidden");
  modalExplainerBtnEl.setAttribute("aria-expanded", "true");
}

function fillAnswerRow(word: string): void {
  modalAnswerWordEl.textContent = word;
  modalAnswerRowEl.classList.remove("hidden");
}

function updateExplainerUi(): void {
  const show = isGameFinished();
  if (show) {
    fillAnswerRow(game.puzzle.word);
  } else {
    modalAnswerRowEl.classList.add("hidden");
    collapseWordExplainer();
  }
}

function hideStatsModal(): void {
  statsModalEl.classList.add("hidden");
}

function renderStatsModal(): void {
  const stats = loadStats();
  const max = maxDistribution(stats);
  const bars = stats.distribution
    .map((count, i) => {
      const pct = Math.round((count / max) * 100);
      return `<div class="stats-bar-row">
        <span>${i + 1}</span>
        <div class="stats-bar-track"><div class="stats-bar-fill" style="width:${pct}%"></div></div>
        <span>${count}</span>
      </div>`;
    })
    .join("");
  const lossPct = Math.round((stats.losses / max) * 100);

  statsBodyEl.innerHTML = `
    <div class="stats-counters">
      <div><div class="stats-counter-value">${stats.gamesPlayed}</div><div class="stats-counter-label">Игр</div></div>
      <div><div class="stats-counter-value">${winRate(stats)}</div><div class="stats-counter-label">Побед %</div></div>
      <div><div class="stats-counter-value">${stats.currentStreak}</div><div class="stats-counter-label">Серия</div></div>
      <div><div class="stats-counter-value">${stats.maxStreak}</div><div class="stats-counter-label">Рекорд</div></div>
    </div>
    <p class="stats-bars-title">Распределение попыток</p>
    ${bars}
    <div class="stats-bar-row">
      <span>X</span>
      <div class="stats-bar-track"><div class="stats-bar-fill loss" style="width:${lossPct}%"></div></div>
      <span>${stats.losses}</span>
    </div>
  `;
}

function showStatsModal(): void {
  renderStatsModal();
  statsModalEl.classList.remove("hidden");
}

function syncStatsIfFinished(): void {
  if (!game || !isGameFinished()) return;
  if (isStatsRecorded(game.puzzle.dateKey)) return;
  recordGameResult(
    game.puzzle.dateKey,
    game.status === "won",
    game.guesses.length,
  );
}

function isGameFinished(): boolean {
  return game.status === "won" || game.status === "lost";
}

function getShareText(): string {
  return buildShareText(
    game.puzzle,
    game.guesses,
    game.status === "won" ? "won" : "lost",
    getGameUrl(),
  );
}

async function copyShareResult(button: HTMLButtonElement): Promise<void> {
  const label = button.textContent;
  try {
    await copyShareText(getShareText());
    button.textContent = "Скопировано!";
    window.setTimeout(() => {
      button.textContent = label;
    }, 2000);
  } catch {
    setMessage("Не удалось скопировать", "error");
  }
}

function updateShareUi(): void {
  shareBtnEl.classList.toggle("hidden", !isGameFinished());
}

function fillShareBlock(): void {
  const url = getGameUrl();
  modalSharePreviewEl.textContent = buildShareGrid(game.guesses, game.puzzle.word);
  modalShareLinkEl.href = url;
  modalShareLinkEl.textContent = url;
}

function showEndModal(title: string, text: string): void {
  modalTitleEl.textContent = title;
  modalTextEl.textContent = text;
  fillAnswerRow(game.puzzle.word);
  fillShareBlock();
  collapseWordExplainer();
  modalShareBlockEl.classList.remove("hidden");
  modalEl.classList.remove("hidden");
  updateShareUi();
}

function boardSizeClass(length: number): string {
  if (length >= 8) return "board--len-8";
  if (length >= 7) return "board--len-7";
  if (length >= 6) return "board--len-6";
  return "board--len-5";
}

function renderBoard(): void {
  const { length } = game.puzzle;
  boardEl.className = `board ${boardSizeClass(length)}`;
  boardEl.style.setProperty("--cols", String(length));

  const rows: string[] = [];

  for (let row = 0; row < MAX_GUESSES; row++) {
    let letters: EvaluatedLetter[] | null = null;
    let raw = "";

    if (row < game.guesses.length) {
      raw = game.guesses[row]!;
      letters = evaluateGuess(raw, game.puzzle.word);
    } else if (row === game.guesses.length) {
      raw = game.current;
    }

    for (let col = 0; col < length; col++) {
      const ch = raw[col]?.toUpperCase() ?? "";
      const state = letters?.[col]?.state ?? "empty";
      const filled = ch ? "filled" : "";
      let rowClass = "";
      if (letters) {
        rowClass = row === revealingRow ? "reveal" : "settled";
      }
      const tilt = ((row * 7 + col * 13) % 21) - 10;
      rows.push(
        `<div class="cell ${state} ${filled} ${rowClass}" data-col="${col}" style="--i:${col};--tilt:${tilt}">${ch}</div>`,
      );
    }
  }

  boardEl.innerHTML = rows.join("");
}

function renderKeyboard(): void {
  keyboardEl.innerHTML = KEYBOARD_ROWS.map((row, rowIndex) => {
    const rowClass = rowIndex === 1 ? "kb-row kb-row--inset" : "kb-row";
    const keys = row
      .map((key) => {
        if (key === "enter") {
          return `<button class="key key-action key-enter" data-key="enter" aria-label="Ввод"><svg class="key-icon enter-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 14 4 9l5-5" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"/><path d="M4 9h10.5a3.5 3.5 0 0 1 0 7H12" stroke="currentColor" stroke-width="2.25" stroke-linecap="round"/></svg><span class="enter-label">Ввод</span></button>`;
        }
        if (key === "backspace") {
          return `<button class="key key-action key-backspace" data-key="backspace" aria-label="Стереть"><svg class="key-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 6H20.5a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5H9l-5.5-5.5L9 6Z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/><path d="m13 9.5-3 3m0-3 3 3" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/></svg></button>`;
        }
        const state = game.keyboard.get(key) ?? "empty";
        const stateClass = state === "empty" ? "" : state;
        return `<button class="key ${stateClass}" data-key="${key}" aria-label="${key.toUpperCase()}">${key.toUpperCase()}</button>`;
      })
      .join("");
    return `<div class="${rowClass}">${keys}</div>`;
  }).join("");
}

function updateSubtitle(): void {
  subtitleEl.textContent = `№${game.puzzle.gameNumber}`;
}

function submitGuess(): void {
  if (game.status !== "playing") return;

  const guess = toDisplay(game.current);
  const { length } = game.puzzle;

  if (guess.length !== length) {
    setMessage(`Нужно слово из ${length} букв`, "error");
    boardEl.classList.add("shake");
    window.setTimeout(() => boardEl.classList.remove("shake"), 400);
    return;
  }

  if (!game.pools[length].guess.has(guess)) {
    const poolSize = game.pools[length].guess.size;
    setMessage(
      poolSize > 0
        ? `Нет в словаре (${length} букв, слов в базе: ${poolSize})`
        : "Нет в словаре",
      "error",
    );
    boardEl.classList.add("shake");
    window.setTimeout(() => boardEl.classList.remove("shake"), 400);
    return;
  }

  game.guesses.push(guess);
  game.current = "";
  revealingRow = game.guesses.length - 1;

  const evaluated = evaluateGuess(guess, game.puzzle.word);
  game.keyboard = mergeKeyboardState(game.keyboard, evaluated);

  if (guess === game.puzzle.word) {
    game.status = "won";
    game.winMessage = pickWinMessage();
    setMessage(`Угадали за ${game.guesses.length}!`, "success");
    syncStatsIfFinished();
    showEndModal(game.winMessage, `Угадали за ${game.guesses.length} попыток`);
  } else if (game.guesses.length >= MAX_GUESSES) {
    game.status = "lost";
    game.loseMessage = pickLoseMessage(guess);
    setMessage(`Слово дня: ${game.puzzle.word}`, "error");
    syncStatsIfFinished();
    showEndModal(game.loseMessage, `Попытки: ${game.guesses.length}/${MAX_GUESSES}`);
  } else {
    setMessage("");
  }

  saveGame();
  renderBoard();
  renderKeyboard();

  window.setTimeout(() => {
    revealingRow = null;
    renderBoard();
  }, 600);
}

function addLetter(letter: string): void {
  if (game.status !== "playing") return;
  if (game.current.length >= game.puzzle.length) return;
  game.current += letter;
  renderBoard();
}

function removeLetter(): void {
  if (game.status !== "playing") return;
  game.current = game.current.slice(0, -1);
  renderBoard();
}

function handleKey(key: string): void {
  if (key === "enter") {
    submitGuess();
    return;
  }
  if (key === "backspace") {
    removeLetter();
    return;
  }
  if (/^[а-я]$/.test(key)) {
    addLetter(key);
  }
}

function bindKeyboard(): void {
  keyboardEl.addEventListener("click", (event) => {
    const target = (event.target as HTMLElement).closest<HTMLButtonElement>("[data-key]");
    if (!target) return;
    handleKey(target.dataset.key!);
  });

  window.addEventListener("keydown", (event) => {
    if (!ageGateEl.classList.contains("hidden")) return;
    if (!statsModalEl.classList.contains("hidden") && event.key === "Escape") {
      hideStatsModal();
      return;
    }
    if (!modalEl.classList.contains("hidden") && event.key === "Enter") {
      hideModal();
      return;
    }

    const key = event.key.toLowerCase();
    if (key === "enter") {
      event.preventDefault();
      submitGuess();
      return;
    }
    if (key === "backspace") {
      event.preventDefault();
      removeLetter();
      return;
    }
    if (key === "ё") {
      event.preventDefault();
      addLetter("е");
      return;
    }
    if (/^[а-я]$/.test(key)) {
      event.preventDefault();
      addLetter(key);
    }
  });
}

function initGame(
  puzzle: DailyPuzzle,
  pools: WordPools,
  lexicon: WordLexicon,
): void {
  const saved = loadSaved(puzzle.dateKey, puzzle.length);
  game = {
    puzzle,
    pools,
    lexicon,
    guesses: saved?.guesses ?? [],
    current: "",
    status: saved?.status ?? "playing",
    keyboard: new Map(),
    loseMessage:
      saved?.status === "lost"
        ? (saved.loseMessage ??
          pickLoseMessage(saved.guesses[saved.guesses.length - 1] ?? ""))
        : null,
    winMessage:
      saved?.status === "won" ? (saved.winMessage ?? pickWinMessage()) : null,
  };

  for (const guess of game.guesses) {
    const evaluated = evaluateGuess(guess, puzzle.word);
    game.keyboard = mergeKeyboardState(game.keyboard, evaluated);
  }

  if (game.status === "won") {
    setMessage(`Вы уже угадали сегодня (${game.guesses.length} попыток)`, "success");
    if (!saved?.winMessage) saveGame();
  } else if (game.status === "lost") {
    setMessage(`Слово дня: ${puzzle.word}`, "error");
    if (!saved?.loseMessage) saveGame();
  }

  syncStatsIfFinished();
  updateShareUi();
  updateExplainerUi();
  updateSubtitle();
  renderBoard();
  renderKeyboard();
}

async function start(): Promise<void> {
  bindKeyboard();
  modalBtnEl.addEventListener("click", hideModal);
  modalExplainerBtnEl.addEventListener("click", toggleWordExplainer);
  modalShareEl.addEventListener("click", () => copyShareResult(modalShareEl));
  statsBtnEl.addEventListener("click", showStatsModal);
  statsCloseEl.addEventListener("click", hideStatsModal);
  statsModalEl.addEventListener("click", (event) => {
    if (event.target === statsModalEl) hideStatsModal();
  });
  shareBtnEl.addEventListener("click", () => {
    fillShareBlock();
    modalShareBlockEl.classList.remove("hidden");
    modalTitleEl.textContent =
      game.status === "won"
        ? (game.winMessage ?? "Ваш результат")
        : (game.loseMessage ?? "Игра окончена");
    modalTextEl.textContent =
      game.status === "won"
        ? `Угадали за ${game.guesses.length} попыток`
        : `Попытки: ${game.guesses.length}/${MAX_GUESSES}`;
    fillAnswerRow(game.puzzle.word);
    collapseWordExplainer();
    modalEl.classList.remove("hidden");
  });

  ageYesEl.addEventListener("click", () => {
    localStorage.setItem(ADULT_KEY, "true");
    ageGateEl.classList.add("hidden");
    boot();
  });

  ageNoEl.addEventListener("click", () => {
    document.body.innerHTML =
      '<main style="padding:2rem;font-family:Inter,sans-serif;color:#eee;background:#121213;min-height:100vh"></main>';
  });

  await boot();
}

async function boot(): Promise<void> {
  try {
    const dicts = await loadDictionaries();
    const pools = buildWordPools(
      dicts.normal,
      dicts.bundle,
      dicts.guessOnlyProfanity,
      dicts.guessExtended,
    );
    const dateKey = getMoscowDateKey();
    const classic = isClassicDay(dateKey);

    if (!classic && !isAdultConfirmed()) {
      ageGateEl.classList.remove("hidden");
      subtitleEl.textContent = "";
      return;
    }

    const puzzle = pickDailyWord(dateKey, pools);
    initGame(puzzle, pools, dicts.lexicon);

    if (import.meta.env.DEV) {
      const sizes = ([5, 6, 7, 8] as const).map(
        (n) => `${n}:${pools[n].guess.size}`,
      );
      console.info(
        `[huerdli] слово дня: ${puzzle.length} букв, пулы ввода — ${sizes.join(", ")}`,
      );
    }
  } catch (error) {
    subtitleEl.textContent = "Ошибка загрузки";
    setMessage(error instanceof Error ? error.message : "Неизвестная ошибка", "error");
  }
}

start();

// Для отладки: window.__HUERDLI__
declare global {
  interface Window {
    __HUERDLI__?: {
      puzzle: DailyPuzzle;
      guessPoolSize: number;
      canGuess: (word: string) => boolean;
    };
  }
}

Object.defineProperty(window, "__HUERDLI__", {
  get() {
    if (!game) return undefined;
    return {
      puzzle: game.puzzle,
      guessPoolSize: game.pools[game.puzzle.length].guess.size,
      canGuess(word: string) {
        const w = toDisplay(word);
        return game.pools[game.puzzle.length].guess.has(w);
      },
    };
  },
});
