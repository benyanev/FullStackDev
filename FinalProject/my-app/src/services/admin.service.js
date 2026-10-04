import { request, get } from './httpClient';

/**
 * Fetch all pending reports (admin only).
 * @returns {Promise<Array>} Report objects with post and user info.
 */
export async function fetchReports() {
  return get('/admin/reports', 'Failed to fetch reports');
}

/**
 * Mark a report as resolved or dismissed (admin only).
 * @param {number} reportId
 * @param {'resolved'|'dismissed'} status
 * @returns {Promise<{message: string}>}
 */
export async function updateReport(reportId, status) {
  return request(`/admin/reports/${reportId}`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  }, 'Failed to update report');
}

/**
 * Delete a post (admin only). Its reports are deleted with it.
 * @param {number} postId
 * @returns {Promise<{message: string}>}
 */
export async function deletePostAsAdmin(postId) {
  return request(`/admin/posts/${postId}`, { method: 'DELETE' }, 'Failed to delete post');
}

/**
 * Fetch users with their role and ban status (admin only).
 * @returns {Promise<Array>} User objects.
 */
export async function fetchAdminUsers() {
  return get('/admin/users', 'Failed to fetch users');
}

/**
 * Ban or unban a user (admin only).
 * @param {number} userId
 * @param {boolean} banned
 * @returns {Promise<{message: string}>}
 */
export async function setUserBanned(userId, banned) {
  return request(`/admin/users/${userId}/ban`, {
    method: 'PUT',
    body: JSON.stringify({ banned }),
  }, 'Failed to update user');
}

/**
 * Promote a user to moderator or demote them (admin only).
 * @param {number} userId
 * @param {'user'|'admin'} role
 * @returns {Promise<{message: string}>}
 */
export async function setUserRole(userId, role) {
  return request(`/admin/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  }, 'Failed to update user');
}
