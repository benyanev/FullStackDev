import { get } from './httpClient';

/**
 * Fetch a page of users.
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of users to fetch.
 * @returns {Promise<Array>} Array of user objects.
 */
export async function fetchUsers(start = 0, limit = 100) {
  return get(`/users?_start=${start}&_limit=${limit}`, 'Failed to fetch users');
}

/**
 * Fetch a single user by ID.
 * @param {number} userId
 * @returns {Promise<Object>} User object.
 */
export async function fetchUser(userId) {
  return get(`/users/${userId}`, `Failed to fetch user ${userId}`);
}
