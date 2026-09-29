import { requestFormData } from './httpClient';

/**
 * Upload a post image file.
 * @param {File} file - The image file to upload.
 * @returns {Promise<{url: string}>} The uploaded file URL.
 */
export async function uploadPostImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  return requestFormData('/upload/image', formData, 'Image upload failed');
}

/**
 * Upload a post video file (mp4/webm, max 50 MB).
 * @param {File} file - The video file to upload.
 * @returns {Promise<{url: string}>} The uploaded file URL.
 */
export async function uploadPostVideo(file) {
  const formData = new FormData();
  formData.append('file', file);
  return requestFormData('/upload/video', formData, 'Video upload failed');
}
