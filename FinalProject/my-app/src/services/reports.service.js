import { request } from './httpClient';

/**
 * Report a post for moderator review.
 * @param {number} postId
 * @param {string} reason - Why the post is being reported.
 * @returns {Promise<{message: string}>}
 */
export async function reportPost(postId, reason) {
  return request('/reports', {
    method: 'POST',
    body: JSON.stringify({ post_id: postId, reason }),
  }, 'Failed to report post');
}
