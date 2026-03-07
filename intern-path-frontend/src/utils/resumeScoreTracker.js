const KEY_PREFIX = "internpath_resume_score";

const getStorageKey = (userId) => `${KEY_PREFIX}:${userId || "guest"}`;

export const getStoredResumeScore = (userId) => {
  const rawValue = localStorage.getItem(getStorageKey(userId));
  const parsed = Number(rawValue);
  if (!Number.isFinite(parsed)) return null;
  return Math.max(0, Math.min(100, Math.round(parsed)));
};

export const setStoredResumeScore = (userId, score) => {
  const numericScore = Number(score);
  if (!Number.isFinite(numericScore)) return;
  const normalized = Math.max(0, Math.min(100, Math.round(numericScore)));
  localStorage.setItem(getStorageKey(userId), String(normalized));
};
