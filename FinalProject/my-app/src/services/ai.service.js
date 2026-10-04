import { request } from './httpClient';

/**
 * Fix spelling and grammar of a text (plain text or editor HTML).
 * @param {string} text
 * @returns {Promise<{text: string}>}
 */
export async function autocorrectText(text) {
  return request('/ai/autocorrect', {
    method: 'POST',
    body: JSON.stringify({ text }),
  }, 'AI autocorrect failed');
}

/**
 * Ask the AI to write a post about a topic.
 * @param {string} topic
 * @returns {Promise<{title: string, body: string}>} body is simple HTML.
 */
export async function suggestPost(topic) {
  return request('/ai/suggest-post', {
    method: 'POST',
    body: JSON.stringify({ topic }),
  }, 'AI post suggestion failed');
}

/**
 * Ask the AI to propose a comment based on the post and its comments.
 * @param {number} postId
 * @returns {Promise<{text: string}>}
 */
export async function suggestComment(postId) {
  return request('/ai/suggest-comment', {
    method: 'POST',
    body: JSON.stringify({ post_id: postId }),
  }, 'AI comment suggestion failed');
}
