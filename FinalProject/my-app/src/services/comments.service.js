import { request, get } from './httpClient';

/**
 * Create a new comment on a post.
 * Requires an active session cookie.
 * @param {number} postId
 * @param {string} body - Comment text.
 * @param {number|null} [parentId=null] - Optional parent comment ID for nesting.
 * @returns {Promise<{id: number, message: string}>}
 */
export async function createComment(postId, body, parentId = null) {
  return request(`/posts/${postId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ body, parent_id: parentId }),
  }, 'Failed to create comment');
}

/**
 * Fetch all comments for a post.
 * @param {number} postId
 * @returns {Promise<{comments: Array, count: number}>}
 */
export async function fetchComments(postId) {
  return get(`/posts/${postId}/comments`, 'Failed to fetch comments');
}
