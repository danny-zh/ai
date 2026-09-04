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
   * Fetch JSON from a protected habit API endpoint.
   * @param {string} path API path to request.
   * @param {RequestInit & {session?: {access_token: string}}} options Fetch options with an optional session.
   * @returns {Promise<object|null>} Parsed JSON response or null for no-content responses.
   */
  async function fetch_json(path, options = {}) {
    const session = options.session || null;
    const access_token = session && session.access_token;
    const headers = {
      'Content-Type': 'application/json',
      ...(access_token ? { Authorization: `Bearer ${access_token}` } : {}),
      ...(options.headers || {})
    };
    const { session: _session, ...fetch_options } = options;
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetch_options,
      headers: {
        ...headers
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
      const error = new Error(message);
      error.status = response.status;
      throw error;
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  /**
   * List backend-shaped habits for a user.
   * @param {number} user_id Authenticated user identifier.
   * @param {{access_token: string}} session Authenticated session.
   * @returns {Promise<Array<{id: number, name: string, color: string, description: string|null, id_user: number}>>} Habit records.
   */
  function get_habits(user_id, session) {
    return fetch_json(`/users/${user_id}/habits`, { session });
  }

  /**
   * Create a backend-shaped habit for a user.
   * @param {number} user_id Authenticated user identifier.
   * @param {{name: string, color: string, description?: string}} payload Habit creation payload.
   * @param {{access_token: string}} session Authenticated session.
   * @returns {Promise<{id: number, name: string, color: string, description: string|null, id_user: number}>} Created habit.
   */
  function create_habit(user_id, payload, session) {
    return fetch_json(`/users/${user_id}/habits`, {
      method: 'POST',
      body: JSON.stringify({
        name: payload.name,
        color: payload.color,
        description: payload.description || null
      }),
      session
    });
  }

  /**
   * Update a backend-shaped habit.
   * @param {number} habit_id Habit identifier.
   * @param {{name?: string, color?: string, description?: string|null}} payload Habit update payload.
   * @param {{access_token: string}} session Authenticated session.
   * @returns {Promise<{id: number, name: string, color: string, description: string|null, id_user: number}>} Updated habit.
   */
  function update_habit(habit_id, payload, session) {
    return fetch_json(`/habits/${habit_id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
      session
    });
  }

  /**
   * Delete an owned habit.
   * @param {number} habit_id Habit identifier.
   * @param {{access_token: string}} session Authenticated session.
   * @returns {Promise<boolean>} True after deletion succeeds.
   */
  async function delete_habit(habit_id, session) {
    await fetch_json(`/habits/${habit_id}`, {
      method: 'DELETE',
      session
    });
    return true;
  }

  /**
   * List backend-shaped logs for a habit.
   * @param {number} habit_id Habit identifier.
   * @param {{access_token: string}} session Authenticated session.
   * @returns {Promise<Array<{id_habit: number, id_user: number, habit_duration: number, log_date: string}>>} Habit log records.
   */
  function get_habit_logs(habit_id, session) {
    return fetch_json(`/habits/${habit_id}/logs`, { session });
  }

  /**
   * Create or replace one habit log entry.
   * @param {number} habit_id Habit identifier.
   * @param {string} log_date Date key in yyyy-mm-dd format.
   * @param {{access_token: string}} session Authenticated session.
   * @param {number} habit_duration Completed duration in minutes.
   * @returns {Promise<{id_habit: number, id_user: number, habit_duration: number, log_date: string}>} Habit log record.
   */
  function upsert_habit_log(habit_id, log_date, session, habit_duration = 60) {
    return fetch_json(`/habits/${habit_id}/logs`, {
      method: 'POST',
      body: JSON.stringify({ log_date, habit_duration }),
      session
    });
  }

  /**
   * Delete one habit log entry.
   * @param {number} habit_id Habit identifier.
   * @param {string} log_date Date key in yyyy-mm-dd format.
   * @param {{access_token: string}} session Authenticated session.
   * @returns {Promise<boolean>} True after deletion succeeds.
   */
  async function delete_habit_log(habit_id, log_date, session) {
    await fetch_json(`/habits/${habit_id}/logs/${log_date}`, {
      method: 'DELETE',
      session
    });
    return true;
  }

  return {
    create_habit,
    delete_habit,
    delete_habit_log,
    fetch_json,
    get_habits,
    get_habit_logs,
    update_habit,
    upsert_habit_log
  };
});
