(function (global, factory) {
  const api = factory();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  global.HabitTracker = global.HabitTracker || {};
  Object.assign(global.HabitTracker, api);
})(typeof window !== 'undefined' ? window : globalThis, function () {
  class Habit {
    constructor({ id, name, color, entries = {} }) {
      this.id = id || `habit-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      this.name = name || 'Untitled habit';
      this.color = color || '#4f46e5';
      this.entries = entries;
    }

    toggle_day(date_key) {
      this.entries[date_key] = !this.entries[date_key];
      return this.entries[date_key];
    }

    is_done_on(date_key) {
      return Boolean(this.entries[date_key]);
    }

    to_json() {
      return {
        id: this.id,
        name: this.name,
        color: this.color,
        entries: this.entries
      };
    }
  }

  return { Habit };
});
