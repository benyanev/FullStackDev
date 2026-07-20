import { request, get } from './httpClient';

/**
 * Follow a user.
 * @param {number} userId - The user ID to follow.
 * @returns {Promise<Object>} { message, following: true }
 */
export async function followUser(userId) {
  return request(`/users/${userId}/follow`, { method: 'POST' }, 'Failed to follow user');
}

/**
 * Unfollow a user.
 * @param {number} userId - The user ID to unfollow.
 * @returns {Promise<Object>} { message, following: false }
 */
export async function unfollowUser(userId) {
  return request(`/users/${userId}/follow`, { method: 'DELETE' }, 'Failed to unfollow user');
}

/**
 * Get the followers of a user.
 * @param {number} userId
 * @returns {Promise<{count: number, users: Array}>}
 */
export async function fetchFollowers(userId) {
  return get(`/users/${userId}/followers`, 'Failed to fetch followers');
}

/**
 * Get the users that a user is following.
 * @param {number} userId
 * @returns {Promise<{count: number, users: Array}>}
 */
export async function fetchFollowing(userId) {
  return get(`/users/${userId}/following`, 'Failed to fetch following');
}

/**
 * Check if the current authenticated user follows a target user.
 * @param {number} userId - Target user ID.
 * @returns {Promise<boolean>} True if following.
 */
export async function checkIsFollowing(userId) {
  try {
    const data = await get(`/users/${userId}/is-following`);
    return data.following;
  } catch {
    return false;
  }
}
