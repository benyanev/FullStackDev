import { request, get } from './httpClient';

/**
 * Sign up a new user. The server sets a session cookie automatically.
 * @param {string} name
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{user: Object}>}
 */
export async function signupUser(name, email, password) {
  return request('/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  }, 'Signup failed');
}

/**
 * Log in an existing user. The server sets a session cookie automatically.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{user: Object}>}
 */
export async function loginUser(email, password) {
  return request('/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  }, 'Login failed');
}

/**
 * Log out the current user by destroying the server-side session.
 * @returns {Promise<{message: string}>}
 */
export async function logoutUser() {
  return request('/logout', { method: 'POST' }, 'Logout failed');
}

/**
 * Fetch the currently authenticated user via the session cookie.
 * Returns null if the session is invalid or expired.
 * @returns {Promise<Object|null>} User object or null.
 */
export async function fetchCurrentUser() {
  try {
    const data = await get('/me');
    return data.user || null;
  } catch {
    return null;
  }
}
