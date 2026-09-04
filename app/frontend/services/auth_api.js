(function (global, factory) {
  const api = factory();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  global.HabitTracker = global.HabitTracker || {};
  Object.assign(global.HabitTracker, api);
})(typeof window !== 'undefined' ? window : globalThis, function () {
  const API_BASE_URL = 'http://localhost:8001';

  /**
   * Fetch JSON from the authentication API.
   * @param {string} path API path to request.
   * @param {RequestInit} options Fetch options.
   * @returns {Promise<object>} Parsed JSON response.
   */
  async function fetch_json(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });

    if (!response.ok) {
      let message = `Request failed: ${response.status}`;
      try {
        const payload = await response.json();
        message = payload.detail || message;
      } catch (error) {
        message = response.statusText || message;
      }
      throw new Error(message);
    }

    return response.json();
  }

  /**
   * Register a user account.
   * @param {string} username Unique login name.
   * @param {string} email Account email address.
   * @param {string} password Account password.
   * @returns {Promise<{id: number, username: string, email: string}>} Registered user.
   */
  function register_user(username, email, password) {
    return fetch_json('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password })
    });
  }

  /**
   * Log in a user account.
   * @param {string} username Account login name.
   * @param {string} password Account password.
   * @returns {Promise<{access_token: string, token_type: string, user_id: number, username: string}>} Token session.
   */
  function login_user(username, password) {
    return fetch_json('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
  }

  return {
    login_user,
    register_user
  };
});