(function (global, factory) {
  const api = factory();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  global.HabitTracker = global.HabitTracker || {};
  Object.assign(global.HabitTracker, api);
})(typeof window !== 'undefined' ? window : globalThis, function () {
  function create_app_state() {
    return {
      habits: [],
      selected_month: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
      loading: false,
      error: '',
      on_delete_habit: null
    };
  }

  function render_habit_list(app_state) {
    const list = document.getElementById('habit-list');
    if (!list) {
      return;
    }

    list.innerHTML = '';

    if (!app_state.habits.length) {
      const empty = document.createElement('li');
      empty.className = 'empty-state';
      empty.textContent = 'No habits yet.';
      list.appendChild(empty);
      return;
    }

    app_state.habits.forEach((habit) => {
      const item = document.createElement('li');
      item.className = 'habit-item';
      item.style.borderLeft = `4px solid ${habit.color}`;

      const meta = document.createElement('div');
      meta.className = 'habit-meta';

      const swatch = document.createElement('span');
      swatch.className = 'habit-swatch';
      swatch.style.background = habit.color;

      const text_group = document.createElement('div');
      text_group.className = 'habit-text-group';

      const name = document.createElement('span');
      name.className = 'habit-name';
      name.textContent = habit.name;

      const summary = document.createElement('span');
      summary.className = 'habit-summary';

      const month_year = new Date(app_state.selected_month.getFullYear(), app_state.selected_month.getMonth(), 1);
      const month_start = new Date(month_year.getFullYear(), month_year.getMonth(), 1);
      const month_end = new Date(month_year.getFullYear(), month_year.getMonth() + 1, 0);
      const total_days_in_month = month_end.getDate();
      let completed_days = 0;

      Object.entries(habit.entries || {}).forEach(([date_key, is_done]) => {
        const date = new Date(`${date_key}T00:00:00`);
        const within_month = date >= month_start && date <= month_end;
        if (within_month && is_done) {
          completed_days += 1;
        }
      });

      summary.textContent = `${completed_days}/${total_days_in_month} completed`;

      text_group.appendChild(name);
      text_group.appendChild(summary);

      meta.appendChild(swatch);
      meta.appendChild(text_group);

      const actions = document.createElement('div');
      actions.className = 'habit-actions';

      const delete_button = document.createElement('button');
      delete_button.type = 'button';
      delete_button.className = 'icon-button';
      delete_button.textContent = 'Delete';
      delete_button.addEventListener('click', () => {
        app_state.on_delete_habit(habit.id);
      });

      actions.appendChild(delete_button);
      item.appendChild(meta);
      item.appendChild(actions);
      list.appendChild(item);
    });
  }

  function set_error_message(message) {
    const error = document.getElementById('error-message');
    if (error) {
      error.textContent = message;
    }
  }

  return {
    create_app_state,
    render_habit_list,
    set_error_message
  };
});
