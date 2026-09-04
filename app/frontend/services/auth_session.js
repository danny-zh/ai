(function (global, factory) {
  const api = factory(global);

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  global.HabitTracker = global.HabitTracker || {};
  Object.assign(global.HabitTracker, api);
})(typeof window !== 'undefined' ? window : globalThis, function (global) {
  const storage_keys = {
    access_token: 'habit_tracker_access_token',
    user_id: 'habit_tracker_user_id',
    username: 'habit_tracker_username'
  };

  /**
   * Return browser storage when it is available.
   * @returns {Storage|null} Local storage or null.
   */
  function get_storage() {
    if (!global.localStorage) {
      return null;
    }
    return global.localStorage;
  }

  /**
   * Persist an authenticated user session.
   * @param {{access_token: string, user_id: number, username: string}} session Auth session returned by the API.
   * @returns {void}
   */
  function save_session(session) {
    const storage = get_storage();
    if (!storage) {
      return;
    }

    storage.setItem(storage_keys.access_token, session.access_token);
    storage.setItem(storage_keys.user_id, String(session.user_id));
    storage.setItem(storage_keys.username, session.username);
  }

  /**
   * Read the saved authenticated user session.
   * @returns {{access_token: string, user_id: number, username: string}|null} Saved session or null.
   */
  function get_session() {
    const storage = get_storage();
    if (!storage) {
      return null;
    }

    const access_token = storage.getItem(storage_keys.access_token);
    const stored_user_id = storage.getItem(storage_keys.user_id);
    const user_id = Number(stored_user_id);
    const username = storage.getItem(storage_keys.username);

    if (!access_token || !stored_user_id || !Number.isInteger(user_id) || !username) {
      return null;
    }

    return { access_token, user_id, username };
  }

  /**
   * Remove any saved authenticated user session.
   * @returns {void}
   */
  function clear_session() {
    const storage = get_storage();
    if (!storage) {
      return;
    }

    storage.removeItem(storage_keys.access_token);
    storage.removeItem(storage_keys.user_id);
    storage.removeItem(storage_keys.username);
  }

  /**
   * Report whether a complete session is saved.
   * @returns {boolean} True when a usable session exists.
   */
  function is_authenticated() {
    return Boolean(get_session());
  }

  return {
    clear_session,
    get_session,
    is_authenticated,
    save_session,
    storage_keys
  };
});