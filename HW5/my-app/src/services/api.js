const BASE_URL = 'http://localhost:5000/api';

/**
 * Default fetch options — all requests include credentials (cookies)
 * so the session cookie is sent automatically by the browser.
 */
const DEFAULT_OPTIONS = { credentials: 'include' };

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

/**
 * Sign up a new user. The server sets a session cookie automatically.
 * @param {string} name
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{user: Object}>}
 */
export async function signupUser(name, email, password) {
  const response = await fetch(`${BASE_URL}/signup`, {
    ...DEFAULT_OPTIONS,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Signup failed');
  }
  return data;
}

/**
 * Log in an existing user. The server sets a session cookie automatically.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{user: Object}>}
 */
export async function loginUser(email, password) {
  const response = await fetch(`${BASE_URL}/login`, {
    ...DEFAULT_OPTIONS,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Login failed');
  }
  return data;
}

/**
 * Log out the current user by destroying the server-side session.
 * @returns {Promise<{message: string}>}
 */
export async function logoutUser() {
  const response = await fetch(`${BASE_URL}/logout`, {
    ...DEFAULT_OPTIONS,
    method: 'POST',
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Logout failed');
  }
  return data;
}

/**
 * Fetch the currently authenticated user via the session cookie.
 * Returns null if the session is invalid or expired.
 * @returns {Promise<Object|null>} User object or null.
 */
export async function fetchCurrentUser() {
  try {
    const response = await fetch(`${BASE_URL}/me`, DEFAULT_OPTIONS);
    if (!response.ok) return null;
    const data = await response.json();
    return data.user || null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Posts
// ---------------------------------------------------------------------------

/**
 * Fetch a page of posts (with author email already included).
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of posts to fetch.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function fetchPosts(start = 0, limit = 10) {
  const response = await fetch(
    `${BASE_URL}/posts?_start=${start}&_limit=${limit}`,
    DEFAULT_OPTIONS,
  );
  if (!response.ok) {
    throw new Error('Failed to fetch posts');
  }
  return response.json();
}

/**
 * Fetch a page of posts for a specific user.
 * @param {number} userId
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of posts to fetch.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function fetchUserPosts(userId, start = 0, limit = 10) {
  const response = await fetch(
    `${BASE_URL}/posts?userId=${userId}&_start=${start}&_limit=${limit}`,
    DEFAULT_OPTIONS,
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch posts for user ${userId}`);
  }
  return response.json();
}

/**
 * Create a new post (requires an active session cookie).
 * @param {string} title
 * @param {string} body
 * @returns {Promise<Object>} The created post response.
 */
export async function createPost(title, body) {
  const response = await fetch(`${BASE_URL}/posts`, {
    ...DEFAULT_OPTIONS,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, body }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Failed to create post');
  }
  return data;
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

/**
 * Fetch a page of users.
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of users to fetch.
 * @returns {Promise<Array>} Array of user objects.
 */
export async function fetchUsers(start = 0, limit = 100) {
  const response = await fetch(
    `${BASE_URL}/users?_start=${start}&_limit=${limit}`,
    DEFAULT_OPTIONS,
  );
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  return response.json();
}

/**
 * Fetch a single user by ID (used for "Posts by [name]" heading).
 * @param {number} userId
 * @returns {Promise<Object>} User object.
 */
export async function fetchUser(userId) {
  const response = await fetch(`${BASE_URL}/users/${userId}`, DEFAULT_OPTIONS);
  if (!response.ok) {
    throw new Error(`Failed to fetch user ${userId}`);
  }
  return response.json();
}
