import { request, get } from './httpClient';

/**
 * Fetch a page of posts (with author email already included).
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of posts to fetch.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function fetchPosts(start = 0, limit = 10) {
  return get(`/posts?_start=${start}&_limit=${limit}`, 'Failed to fetch posts');
}

/**
 * Fetch a page of posts for a specific user.
 * @param {number} userId
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of posts to fetch.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function fetchUserPosts(userId, start = 0, limit = 10) {
  return get(
    `/posts?userId=${userId}&_start=${start}&_limit=${limit}`,
    `Failed to fetch posts for user ${userId}`,
  );
}

/**
 * Fetch a page of posts from users the current user follows.
 * Requires an active session cookie.
 * @param {number} start - Offset (0-based).
 * @param {number} limit - Number of posts to fetch.
 * @returns {Promise<Array>} Array of post objects.
 */
export async function fetchFollowingPosts(start = 0, limit = 10) {
  return get(
    `/posts/following?_start=${start}&_limit=${limit}`,
    'Failed to fetch following posts',
  );
}

/**
 * Create a new post (requires an active session cookie).
 * @param {string} title
 * @param {string} body
 * @param {string} [imageUrl] - Optional URL of an uploaded image.
 * @param {string} [videoUrl] - Optional URL of an uploaded video.
 * @returns {Promise<Object>} The created post response.
 */
export async function createPost(title, body, imageUrl = '', videoUrl = '') {
  return request('/posts', {
    method: 'POST',
    body: JSON.stringify({ title, body, image_url: imageUrl, video_url: videoUrl }),
  }, 'Failed to create post');
}
