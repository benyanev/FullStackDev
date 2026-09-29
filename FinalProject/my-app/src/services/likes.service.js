import { request, get } from './httpClient';

/**
 * Toggle a like on a post (like if not liked, unlike if liked).
 * Requires an active session cookie.
 * @param {number} postId
 * @returns {Promise<{liked: boolean, likeCount: number}>}
 */
export async function toggleLike(postId) {
  return request(`/posts/${postId}/like`, {
    method: 'POST',
  }, 'Failed to toggle like');
}

/**
 * Get the like count and whether the current user has liked a post.
 * @param {number} postId
 * @returns {Promise<{liked: boolean, likeCount: number}>}
 */
export async function fetchPostLikes(postId) {
  return get(`/posts/${postId}/likes`, 'Failed to fetch likes');
}
