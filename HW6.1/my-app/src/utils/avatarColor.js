/**
 * Generate a consistent HSL color string from a name.
 * Used across the app to give each user a unique avatar background color.
 *
 * @param {string} name - The user's display name.
 * @returns {string} HSL color string, e.g. "hsl(210, 55%, 50%)".
 */
export function getAvatarColor(name) {
  const hue = [...name].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360;
  return `hsl(${hue}, 55%, 50%)`;
}
