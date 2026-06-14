const BASE_URL = 'http://localhost:5000/api';

const DEFAULT_OPTIONS = { credentials: 'include' };

/**
 * Send a JSON request and return the parsed response.
 * Throws an Error with the server message when the response is not OK.
 *
 * @param {string}  endpoint     - Path appended to BASE_URL (e.g. '/login').
 * @param {object}  [options={}] - Extra fetch options (method, body, etc.).
 * @param {string}  [fallbackError='Request failed'] - Default error message.
 * @returns {Promise<any>} Parsed JSON body.
 */
export async function request(endpoint, options = {}, fallbackError = 'Request failed') {
  const headers = { 'Content-Type': 'application/json', ...options.headers };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...DEFAULT_OPTIONS,
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || fallbackError);
  }

  return data;
}

/**
 * Send a request without the Content-Type header (browser sets it for FormData).
 * Used for file uploads.
 *
 * @param {string}   endpoint       - Path appended to BASE_URL.
 * @param {FormData} formData       - The form data to send.
 * @param {string}   [fallbackError='Upload failed'] - Default error message.
 * @returns {Promise<any>} Parsed JSON body.
 */
export async function requestFormData(endpoint, formData, fallbackError = 'Upload failed') {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...DEFAULT_OPTIONS,
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || fallbackError);
  }

  return data;
}

/**
 * Send a GET request and return the parsed JSON.
 * Throws on non-OK responses.
 *
 * @param {string} endpoint       - Path appended to BASE_URL.
 * @param {string} [fallbackError='Request failed'] - Default error message.
 * @returns {Promise<any>} Parsed JSON body.
 */
export async function get(endpoint, fallbackError = 'Request failed') {
  const response = await fetch(`${BASE_URL}${endpoint}`, DEFAULT_OPTIONS);

  if (!response.ok) {
    throw new Error(fallbackError);
  }

  return response.json();
}
