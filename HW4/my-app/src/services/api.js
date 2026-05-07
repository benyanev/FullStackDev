const BASE_URL = 'http://localhost:5000/api';

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

/**
 * Sign up a new user.
 * @param {string} name
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{token: string, user: Object}>}
 */
export async function signupUser(name, email, password) {
  const response = await fetch(`${BASE_URL}/signup`, {
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
 * Log in an existing user.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{token: string, user: Object}>}
 */
export async function loginUser(email, password) {
  const response = await fetch(`${BASE_URL}/login`, {
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
    `${BASE_URL}/posts?_start=${start}&_limit=${limit}`
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
    `${BASE_URL}/posts?userId=${userId}&_start=${start}&_limit=${limit}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch posts for user ${userId}`);
  }
  return response.json();
}

/**
 * Create a new post (requires authentication).
 * @param {string} title
 * @param {string} body
 * @param {string} token - JWT auth token.
 * @returns {Promise<Object>} The created post response.
 */
export async function createPost(title, body, token) {
  const response = await fetch(`${BASE_URL}/posts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
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
    `${BASE_URL}/users?_start=${start}&_limit=${limit}`
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
  const response = await fetch(`${BASE_URL}/users/${userId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user ${userId}`);
  }
  return response.json();
}
