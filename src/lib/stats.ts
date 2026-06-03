/** Первый день публикации — игра №1. */
export const GAME_EPOCH = "2026-06-03";

export type Stats = {
  gamesPlayed: number;
  gamesWon: number;
  currentStreak: number;
  maxStreak: number;
  /** Попытки 1–6 */
  distribution: [number, number, number, number, number, number];
  losses: number;
  lastPlayedDate: string | null;
  recordedDates: string[];
};

const STATS_KEY = "huerdli-stats-v1";

function emptyStats(): Stats {
  return {
    gamesPlayed: 0,
    gamesWon: 0,
    currentStreak: 0,
    maxStreak: 0,
    distribution: [0, 0, 0, 0, 0, 0],
    losses: 0,
    lastPlayedDate: null,
    recordedDates: [],
  };
}

function parseDateKey(dateKey: string): number {
  const [y, m, d] = dateKey.split("-").map(Number);
  return Date.UTC(y!, m! - 1, d!);
}

export function getGameNumber(dateKey: string): number {
  const diff = Math.round((parseDateKey(dateKey) - parseDateKey(GAME_EPOCH)) / 86_400_000);
  return Math.max(1, diff + 1);
}

function dayBefore(dateKey: string): string {
  const ms = parseDateKey(dateKey) - 86_400_000;
  const d = new Date(ms);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function loadStats(): Stats {
  try {
    const raw = localStorage.getItem(STATS_KEY);
    if (!raw) return emptyStats();
    const parsed = JSON.parse(raw) as Stats;
    return {
      ...emptyStats(),
      ...parsed,
      distribution: parsed.distribution ?? emptyStats().distribution,
      recordedDates: parsed.recordedDates ?? [],
    };
  } catch {
    return emptyStats();
  }
}

export function saveStats(stats: Stats): void {
  localStorage.setItem(STATS_KEY, JSON.stringify(stats));
}

export function isStatsRecorded(dateKey: string): boolean {
  return loadStats().recordedDates.includes(dateKey);
}

export function recordGameResult(
  dateKey: string,
  won: boolean,
  guessCount: number,
): Stats {
  const stats = loadStats();
  if (stats.recordedDates.includes(dateKey)) {
    return stats;
  }

  stats.gamesPlayed += 1;
  stats.recordedDates.push(dateKey);

  if (won) {
    stats.gamesWon += 1;
    const idx = Math.min(Math.max(guessCount, 1), 6) - 1;
    stats.distribution[idx] = (stats.distribution[idx] ?? 0) + 1;

    if (stats.lastPlayedDate === dayBefore(dateKey)) {
      stats.currentStreak += 1;
    } else if (stats.lastPlayedDate !== dateKey) {
      stats.currentStreak = 1;
    }
  } else {
    stats.losses += 1;
    stats.currentStreak = 0;
  }

  stats.maxStreak = Math.max(stats.maxStreak, stats.currentStreak);
  stats.lastPlayedDate = dateKey;
  saveStats(stats);
  return stats;
}

export function winRate(stats: Stats): number {
  if (stats.gamesPlayed === 0) return 0;
  return Math.round((stats.gamesWon / stats.gamesPlayed) * 100);
}

export function maxDistribution(stats: Stats): number {
  const values = [...stats.distribution, stats.losses];
  return Math.max(1, ...values);
}
