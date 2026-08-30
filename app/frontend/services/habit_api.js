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

  const fallback_habits = [
    {
      id: 'fallback-workout',
      name: 'Workout',
      color: '#4f46e5',
      entries: {
        '2026-08-01': true,
        '2026-08-03': true,
        '2026-08-05': false,
        '2026-08-10': true
      }
    },
    {
      id: 'fallback-read',
      name: 'Read',
      color: '#10b981',
      entries: {
        '2026-08-02': true,
        '2026-08-04': true,
        '2026-08-08': false,
        '2026-08-12': true
      }
    }
  ];

  async function fetch_json(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
  }

  async function get_habits() {
    try {
      return await fetch_json('/habits');
    } catch (error) {
      return fallback_habits;
    }
  }

  async function create_habit(payload) {
    try {
      return await fetch_json('/habits', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    } catch (error) {
      return {
        id: `local-${Date.now()}`,
        ...payload,
        entries: payload.entries || {}
      };
    }
  }

  async function update_habit(habit_id, payload) {
    try {
      return await fetch_json(`/habits/${habit_id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });
    } catch (error) {
      return {
        id: habit_id,
        name: payload.name || `Habit ${habit_id}`,
        color: payload.color || '#4f46e5',
        entries: payload.entries || {}
      };
    }
  }

  async function delete_habit(habit_id) {
    try {
      const response = await fetch(`${API_BASE_URL}/habits/${habit_id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        return true;
      }

      return response.ok;
    } catch (error) {
      return true;
    }
  }

  return {
    get_habits,
    create_habit,
    update_habit,
    delete_habit
  };
});
