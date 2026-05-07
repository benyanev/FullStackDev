const BASE_URL = 'https://jsonplaceholder.typicode.com';

// Cache user data to avoid repeated fetches for the same userId
const userCache = {};

/**
 * Fetch a page of posts from all users.
 * @param {number} start - Index to start from (0-based).
 * @param {number} limit - Number of posts to fetch.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function fetchPosts(start = 0, limit = 10) {
  const response = await fetch(
    `${BASE_URL}/posts?_start=${start}&_limit=${limit}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch posts');
  }
  return response.json();
}

/**
 * Fetch a single user by ID (results are cached).
 * @param {number} userId
 * @returns {Promise<Object>} User object (contains email, name, etc.).
 */
export async function fetchUser(userId) {
  if (userCache[userId]) {
    return userCache[userId];
  }
  const response = await fetch(`${BASE_URL}/users/${userId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user ${userId}`);
  }
  const user = await response.json();
  userCache[userId] = user;
  return user;
}
