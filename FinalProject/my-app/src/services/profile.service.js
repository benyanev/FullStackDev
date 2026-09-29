import { request, requestFormData } from './httpClient';

/**
 * Upload a profile picture file.
 * @param {File} file - The image file to upload.
 * @returns {Promise<{url: string}>} The uploaded file URL.
 */
export async function uploadProfilePicture(file) {
  const formData = new FormData();
  formData.append('file', file);
  return requestFormData('/upload/profile-picture', formData, 'Upload failed');
}

/**
 * Update a user's profile (name, bio, profile_picture).
 * @param {number} userId
 * @param {Object} fields - { name?, bio?, profile_picture? }
 * @returns {Promise<{user: Object}>}
 */
export async function updateProfile(userId, fields) {
  return request(`/users/${userId}/profile`, {
    method: 'PUT',
    body: JSON.stringify(fields),
  }, 'Profile update failed');
}
