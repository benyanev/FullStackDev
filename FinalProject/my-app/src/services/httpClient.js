const BASE_URL = '/api';

const DEFAULT_OPTIONS = { credentials: 'include' };

/**
 * Read the response body as JSON and throw an Error (with `.status`) when the
 * request failed (e.g. 422 = content blocked by moderation).
 *
 * Error pages that are not JSON (e.g. nginx "502 Bad Gateway" or a timeout)
 * fall back to `fallbackError` instead of crashing with "Unexpected token <".
 */
async function handleResponse(response, fallbackError) {
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = new Error(data.error || fallbackError);
    error.status = response.status;
    throw error;
  }

  return data;
}

/**
 * Send a JSON request and return the parsed response.
 * Throws an Error (with `.status`) carrying the server message when the
 * response is not OK.
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

  return handleResponse(response, fallbackError);
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

  return handleResponse(response, fallbackError);
}

/**
 * Send a GET request and return the parsed JSON.
 * Throws (with the server's message and `.status`) on non-OK responses.
 *
 * @param {string} endpoint       - Path appended to BASE_URL.
 * @param {string} [fallbackError='Request failed'] - Default error message.
 * @returns {Promise<any>} Parsed JSON body.
 */
export async function get(endpoint, fallbackError = 'Request failed') {
  const response = await fetch(`${BASE_URL}${endpoint}`, DEFAULT_OPTIONS);
  return handleResponse(response, fallbackError);
}
