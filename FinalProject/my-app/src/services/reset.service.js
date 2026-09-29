import { request } from './httpClient';

/**
 * Request a password reset email.
 * @param {string} email - The user's email address.
 * @returns {Promise<{message: string}>}
 */
export async function requestPasswordReset(email) {
  return request('/reset-request', {
    method: 'POST',
    body: JSON.stringify({ email }),
  }, 'Failed to request password reset');
}

/**
 * Confirm a password reset with a valid token.
 * @param {string} token - The reset token from the email link.
 * @param {string} password - The new password.
 * @returns {Promise<{message: string}>}
 */
export async function confirmPasswordReset(token, password) {
  return request('/reset-confirm', {
    method: 'POST',
    body: JSON.stringify({ token, password }),
  }, 'Failed to reset password');
}
