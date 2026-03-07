const KEY_PREFIX = "internpath_applications_sent";

const getStorageKey = (userId) => `${KEY_PREFIX}:${userId || "guest"}`;

export const getApplicationsSentCount = (userId) => {
  const key = getStorageKey(userId);
  const rawValue = localStorage.getItem(key);
  const parsed = Number(rawValue);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
};

export const incrementApplicationsSentCount = (userId) => {
  const key = getStorageKey(userId);
  const nextValue = getApplicationsSentCount(userId) + 1;
  localStorage.setItem(key, String(nextValue));
  return nextValue;
};
