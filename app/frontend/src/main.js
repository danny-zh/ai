(function () {
  const { Habit } = globalThis.HabitTracker;
  const { render_calendar } = globalThis.HabitTracker;
  const { get_habits, create_habit, delete_habit, update_habit } = globalThis.HabitTracker;
  const { create_app_state, render_habit_list, set_error_message } = globalThis.HabitTracker;

  const app_state = create_app_state();
  app_state.on_delete_habit = handle_delete_habit;

  function sync_habits(new_habits) {
    app_state.habits = new_habits.map((habit) => new Habit(habit));
    render_habit_list(app_state);
    render_calendar({
      habits: app_state.habits,
      month_date: app_state.selected_month,
      on_toggle_day: handle_toggle_day,
      on_delete_habit: handle_delete_habit
    });
  }

  async function load_habits() {
    try {
      app_state.loading = true;
      const habits = await get_habits();
      sync_habits(habits);
    } catch (error) {
      set_error_message(error.message || 'Unable to load habits');
    } finally {
      app_state.loading = false;
    }
  }

  async function handle_submit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const name = form.elements.name.value.trim();
    const color = form.elements.color.value;

    if (!name) {
      set_error_message('Habit name is required.');
      return;
    }

    try {
      const created = await create_habit({ name, color, entries: {} });
      sync_habits([...app_state.habits, new Habit(created)]);
      form.reset();
      form.elements.color.value = '#4f46e5';
      set_error_message('');
    } catch (error) {
      set_error_message(error.message || 'Unable to save habit');
    }
  }

  async function handle_delete_habit(habit_id) {
    try {
      await delete_habit(habit_id);
      const next_habits = app_state.habits.filter((habit) => habit.id !== habit_id);
      sync_habits(next_habits);
      set_error_message('');
    } catch (error) {
      set_error_message(error.message || 'Unable to delete habit');
    }
  }

  async function handle_toggle_day(habit_id, date_key) {
    const habit = app_state.habits.find((entry) => entry.id === habit_id);
    if (!habit) {
      return;
    }

    const next_value = !habit.is_done_on(date_key);

    try {
      const updated = await update_habit(habit_id, { entries: { ...habit.entries, [date_key]: next_value } });
      const next_habits = app_state.habits.map((entry) => {
        if (entry.id === habit_id) {
          return new Habit(updated);
        }
        return entry;
      });

      sync_habits(next_habits);
      set_error_message('');
    } catch (error) {
      set_error_message(error.message || 'Unable to update habit');
    }
  }

  function apply_theme(theme) {
    const is_dark_mode = theme === 'dark';
    document.body.classList.toggle('dark-mode', is_dark_mode);

    const toggle = document.getElementById('theme-toggle');
    if (toggle) {
      toggle.textContent = is_dark_mode ? 'Light mode' : 'Dark mode';
    }

    localStorage.setItem('habit_tracker_theme', theme);
  }

  function attach_event_listeners() {
    const form = document.getElementById('habit-form');
    if (form) {
      form.addEventListener('submit', handle_submit);
    }

    const add_button = document.getElementById('add-habit-button');
    if (add_button) {
      add_button.addEventListener('click', () => {
        document.getElementById('habit-name')?.focus();
      });
    }

    const theme_toggle = document.getElementById('theme-toggle');
    if (theme_toggle) {
      theme_toggle.addEventListener('click', () => {
        const next_theme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        apply_theme(next_theme);
      });
    }

    const prev_button = document.getElementById('prev-month');
    if (prev_button) {
      prev_button.addEventListener('click', () => {
        app_state.selected_month = new Date(app_state.selected_month.getFullYear(), app_state.selected_month.getMonth() - 1, 1);
        render_calendar({
          habits: app_state.habits,
          month_date: app_state.selected_month,
          on_toggle_day: handle_toggle_day,
          on_delete_habit: handle_delete_habit
        });
      });
    }

    const next_button = document.getElementById('next-month');
    if (next_button) {
      next_button.addEventListener('click', () => {
        app_state.selected_month = new Date(app_state.selected_month.getFullYear(), app_state.selected_month.getMonth() + 1, 1);
        render_calendar({
          habits: app_state.habits,
          month_date: app_state.selected_month,
          on_toggle_day: handle_toggle_day,
          on_delete_habit: handle_delete_habit
        });
      });
    }
  }

  const saved_theme = localStorage.getItem('habit_tracker_theme') || 'light';
  apply_theme(saved_theme);
  attach_event_listeners();
  load_habits();
})();
