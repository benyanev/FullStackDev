/**
 * Format an ISO timestamp into a human-readable "time ago" string.
 *
 * @param {string} isoString - ISO 8601 date string from the backend.
 * @returns {string} e.g. "just now", "5 minutes ago", "2 hours ago", "3 days ago"
 */
export function timeAgo(isoString) {
  if (!isoString) return '';

  const now = Date.now();
  const then = new Date(isoString).getTime();
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days !== 1 ? 's' : ''} ago`;
  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks} week${weeks !== 1 ? 's' : ''} ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months} month${months !== 1 ? 's' : ''} ago`;
  const years = Math.floor(days / 365);
  return `${years} year${years !== 1 ? 's' : ''} ago`;
}

/**
 * Check if a string contains HTML tags (indicates rich text content from Tiptap).
 *
 * @param {string} str
 * @returns {boolean}
 */
export function containsHTML(str) {
  return /<[a-z][\s\S]*>/i.test(str);
}
