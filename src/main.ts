import {
  buildWordPools,
  getMoscowDateKey,
  isProfanityDay,
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
import { buildLoseMessage } from "./lib/loseMessages";
import { buildShareGrid, buildShareText, copyShareText, getGameUrl } from "./lib/share";
import {
  isStatsRecorded,
  loadStats,
  maxDistribution,
  recordGameResult,
  winRate,
} from "./lib/stats";
import "./style.css";

const MAX_GUESSES = 6;
const ADULT_KEY = "huerdli-adult-v1";

const KEYBOARD_ROWS = [
  ["й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ"],
  ["ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э"],
  ["enter", "я", "ч", "с", "м", "и", "т", "ь", "б", "ю", "backspace"],
];

type SavedState = {
  dateKey: string;
  length: number;
  guesses: string[];
  status: "playing" | "won" | "lost";
  loseMessage?: string;
};

type GameContext = {
  puzzle: DailyPuzzle;
  pools: WordPools;
  guesses: string[];
  current: string;
  status: "playing" | "won" | "lost";
  keyboard: Map<string, LetterState>;
  loseMessage: string | null;
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
const GAME_STORAGE_VERSION = 2;

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
  };
  localStorage.setItem(storageKey(game.puzzle.dateKey), JSON.stringify(payload));
}

function isAdultConfirmed(): boolean {
  return localStorage.getItem(ADULT_KEY) === "true";
}

function formatDateRu(dateKey: string): string {
  const [y, m, d] = dateKey.split("-").map(Number);
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "Europe/Moscow",
  }).format(new Date(Date.UTC(y!, m! - 1, d!)));
}

function setMessage(text: string, kind: "info" | "error" | "success" = "info"): void {
  messageEl.textContent = text;
  messageEl.dataset.kind = kind;
}

function showModal(title: string, text: string): void {
  modalTitleEl.textContent = title;
  modalTextEl.textContent = text;
  modalShareBlockEl.classList.add("hidden");
  modalEl.classList.remove("hidden");
}

function hideModal(): void {
  modalEl.classList.add("hidden");
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
  fillShareBlock();
  modalShareBlockEl.classList.remove("hidden");
  modalEl.classList.remove("hidden");
  updateShareUi();
}

function boardSizeClass(length: number): string {
  return length >= 6 ? "board--len-6" : "board--len-5";
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
  keyboardEl.innerHTML = KEYBOARD_ROWS.map((row) => {
    const keys = row
      .map((key) => {
        if (key === "enter") {
          return `<button class="key key-wide" data-key="enter" aria-label="Ввод"><span class="enter-long">Ввод</span><span class="enter-short" aria-hidden="true">↵</span></button>`;
        }
        if (key === "backspace") {
          return `<button class="key key-wide" data-key="backspace" aria-label="Стереть">⌫</button>`;
        }
        const state = game.keyboard.get(key) ?? "empty";
        const stateClass = state === "empty" ? "" : state;
        return `<button class="key ${stateClass}" data-key="${key}" aria-label="${key.toUpperCase()}">${key.toUpperCase()}</button>`;
      })
      .join("");
    return `<div class="kb-row">${keys}</div>`;
  }).join("");
}

function updateSubtitle(): void {
  const { gameNumber, dateKey } = game.puzzle;
  const parts = [
    `№${gameNumber}`,
    formatDateRu(dateKey),
    "В игре может встречаться нецензурная брань",
  ];
  subtitleEl.textContent = parts.join(" · ");
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
    setMessage("Нет в словаре", "error");
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
    setMessage(`Угадали за ${game.guesses.length}!`, "success");
    syncStatsIfFinished();
    showEndModal("Победа!", `Слово дня: ${game.puzzle.word}`);
  } else if (game.guesses.length >= MAX_GUESSES) {
    game.status = "lost";
    game.loseMessage = buildLoseMessage(guess);
    setMessage("Попытки закончились", "error");
    syncStatsIfFinished();
    showEndModal(game.loseMessage, `Слово дня: ${game.puzzle.word}`);
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

function initGame(puzzle: DailyPuzzle, pools: WordPools): void {
  const saved = loadSaved(puzzle.dateKey, puzzle.length);
  game = {
    puzzle,
    pools,
    guesses: saved?.guesses ?? [],
    current: "",
    status: saved?.status ?? "playing",
    keyboard: new Map(),
    loseMessage:
      saved?.status === "lost"
        ? (saved.loseMessage ??
          buildLoseMessage(saved.guesses[saved.guesses.length - 1] ?? ""))
        : null,
  };

  for (const guess of game.guesses) {
    const evaluated = evaluateGuess(guess, puzzle.word);
    game.keyboard = mergeKeyboardState(game.keyboard, evaluated);
  }

  if (game.status === "won") {
    setMessage(`Вы уже угадали сегодня (${game.guesses.length} попыток)`, "success");
  } else if (game.status === "lost") {
    setMessage(game.loseMessage ?? "Попытки закончились", "error");
    if (!saved?.loseMessage) saveGame();
  }

  syncStatsIfFinished();
  updateShareUi();
  updateSubtitle();
  renderBoard();
  renderKeyboard();
}

async function start(): Promise<void> {
  bindKeyboard();
  modalBtnEl.addEventListener("click", hideModal);
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
      game.status === "won" ? "Ваш результат" : (game.loseMessage ?? "Игра окончена");
    modalTextEl.textContent =
      game.status === "won"
        ? `Угадали за ${game.guesses.length} попыток`
        : `Слово дня: ${game.puzzle.word}`;
    modalEl.classList.remove("hidden");
  });

  ageYesEl.addEventListener("click", () => {
    localStorage.setItem(ADULT_KEY, "true");
    ageGateEl.classList.add("hidden");
    boot();
  });

  ageNoEl.addEventListener("click", () => {
    document.body.innerHTML =
      '<main style="padding:2rem;font-family:Inter,sans-serif;color:#eee;background:#121213;min-height:100vh">Игра доступна в обычные дни. Заходите в понедельник, среду или пятницу только если готовы к 18+.</main>';
  });

  await boot();
}

async function boot(): Promise<void> {
  try {
    const dicts = await loadDictionaries();
    const pools = buildWordPools(dicts.normal, dicts.profanity);
    const dateKey = getMoscowDateKey();
    const profanity = isProfanityDay();

    if (profanity && !isAdultConfirmed()) {
      ageGateEl.classList.remove("hidden");
      subtitleEl.textContent = `${formatDateRu(dateKey)} · подтвердите возраст`;
      return;
    }

    const puzzle = pickDailyWord(dateKey, profanity, pools);
    initGame(puzzle, pools);
  } catch (error) {
    subtitleEl.textContent = "Ошибка загрузки";
    setMessage(error instanceof Error ? error.message : "Неизвестная ошибка", "error");
  }
}

start();

// Для отладки: window.__HUERDLI__
declare global {
  interface Window {
    __HUERDLI__?: { puzzle: DailyPuzzle };
  }
}

Object.defineProperty(window, "__HUERDLI__", {
  get() {
    return game ? { puzzle: game.puzzle } : undefined;
  },
});
