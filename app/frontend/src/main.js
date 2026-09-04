(function () {
  const { render_calendar } = globalThis.HabitTracker;
  const { get_habits, create_habit, delete_habit, get_habit_logs, upsert_habit_log, delete_habit_log } = globalThis.HabitTracker;
  const { login_user, register_user } = globalThis.HabitTracker;
  const { clear_session, get_session, save_session } = globalThis.HabitTracker;
  const { create_app_state, render_habit_list, set_error_message } = globalThis.HabitTracker;

  const app_state = create_app_state();
  app_state.on_delete_habit = handle_delete_habit;

  function render_authenticated_app() {
    const auth_view = document.getElementById('auth-view');
    const app_view = document.getElementById('app-view');
    const logout_button = document.getElementById('logout-button');
    const add_button = document.getElementById('add-habit-button');
    const username_label = document.getElementById('current-username');

    if (auth_view) {
      auth_view.hidden = Boolean(app_state.session);
    }
    if (app_view) {
      app_view.hidden = !app_state.session;
    }
    if (logout_button) {
      logout_button.hidden = !app_state.session;
    }
    if (add_button) {
      add_button.hidden = !app_state.session;
    }
    if (username_label) {
      username_label.textContent = app_state.current_user ? app_state.current_user.username : '';
      username_label.hidden = !app_state.current_user;
    }
  }

  function render_auth_mode() {
    const login_form = document.getElementById('login-form');
    const register_form = document.getElementById('register-form');
    const login_toggle = document.getElementById('show-login');
    const register_toggle = document.getElementById('show-register');
    const is_login = app_state.auth_mode === 'login';

    if (login_form) {
      login_form.hidden = !is_login;
    }
    if (register_form) {
      register_form.hidden = is_login;
    }
    login_toggle?.setAttribute('aria-pressed', String(is_login));
    register_toggle?.setAttribute('aria-pressed', String(!is_login));
  }

  function render_app() {
    render_habit_list(app_state);
    render_calendar({
      habits: app_state.habits,
      habit_logs_by_habit_id: app_state.habit_logs_by_habit_id,
      month_date: app_state.selected_month,
      on_toggle_day: handle_toggle_day
    });
    render_authenticated_app();
    render_auth_mode();
  }

  function sync_habits(new_habits, habit_logs_by_habit_id = app_state.habit_logs_by_habit_id) {
    app_state.habits = new_habits;
    app_state.habit_logs_by_habit_id = habit_logs_by_habit_id;
    render_app();
  }

  async function load_habits() {
    if (!app_state.session) {
      render_app();
      return;
    }

    try {
      app_state.loading = true;
      const habits = await get_habits(app_state.session.user_id, app_state.session);
      const logs_by_habit_id = {};
      await Promise.all(habits.map(async (habit) => {
        logs_by_habit_id[habit.id] = await get_habit_logs(habit.id, app_state.session);
      }));
      sync_habits(habits, logs_by_habit_id);
    } catch (error) {
      handle_auth_error(error, 'Unable to load habits');
    } finally {
      app_state.loading = false;
    }
  }

  async function handle_submit(event) {
    event.preventDefault();

    if (!app_state.session) {
      set_error_message('Please log in before creating habits.');
      return;
    }

    const form = event.currentTarget;
    const name = form.elements.name.value.trim();
    const color = form.elements.color.value;
    const description = form.elements.description.value.trim();

    if (!name) {
      set_error_message('Habit name is required.');
      return;
    }

    try {
      const created = await create_habit(app_state.session.user_id, { name, color, description }, app_state.session);
      sync_habits([...app_state.habits, created], {
        ...app_state.habit_logs_by_habit_id,
        [created.id]: []
      });
      form.reset();
      form.elements.color.value = '#4f46e5';
      set_error_message('');
    } catch (error) {
      set_error_message(error.message || 'Unable to save habit');
    }
  }

  async function handle_delete_habit(habit_id) {
    if (!app_state.session) {
      set_error_message('Please log in before deleting habits.');
      return;
    }

    try {
      await delete_habit(habit_id, app_state.session);
      const next_habits = app_state.habits.filter((habit) => habit.id !== habit_id);
      const next_logs_by_habit_id = { ...app_state.habit_logs_by_habit_id };
      delete next_logs_by_habit_id[habit_id];
      sync_habits(next_habits, next_logs_by_habit_id);
      set_error_message('');
    } catch (error) {
      handle_auth_error(error, 'Unable to delete habit');
    }
  }

  async function handle_toggle_day(habit_id, date_key) {
    if (!app_state.session) {
      set_error_message('Please log in before tracking habits.');
      return;
    }

    const habit = app_state.habits.find((entry) => entry.id === habit_id);
    if (!habit) {
      return;
    }

    const existing_logs = app_state.habit_logs_by_habit_id[habit_id] || [];
    const existing_log = existing_logs.find((log) => log.log_date === date_key);

    try {
      let next_logs;
      if (existing_log) {
        await delete_habit_log(habit_id, date_key, app_state.session);
        next_logs = existing_logs.filter((log) => log.log_date !== date_key);
      } else {
        const created_log = await upsert_habit_log(habit_id, date_key, app_state.session);
        next_logs = [...existing_logs, created_log];
      }

      sync_habits(app_state.habits, {
        ...app_state.habit_logs_by_habit_id,
        [habit_id]: next_logs
      });
      set_error_message('');
    } catch (error) {
      handle_auth_error(error, 'Unable to update habit');
    }
  }

  function set_auth_session(session) {
    app_state.session = session;
    app_state.current_user = session ? { id: session.user_id, username: session.username } : null;
    render_app();
  }

  function handle_auth_error(error, fallback_message) {
    if (error.status === 401 || error.status === 403) {
      clear_session();
      app_state.habits = [];
      app_state.habit_logs_by_habit_id = {};
      set_auth_session(null);
      set_error_message('Your session expired. Please log in again.');
      return;
    }

    set_error_message(error.message || fallback_message);
  }

  async function handle_login_submit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const username = form.elements.username.value.trim();
    const password = form.elements.password.value;

    try {
      const session = await login_user(username, password);
      save_session(session);
      set_auth_session(session);
      form.reset();
      set_error_message('');
      await load_habits();
    } catch (error) {
      set_error_message(error.message || 'Unable to log in');
    }
  }

  async function handle_register_submit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const username = form.elements.username.value.trim();
    const email = form.elements.email.value.trim();
    const password = form.elements.password.value;

    try {
      await register_user(username, email, password);
      const session = await login_user(username, password);
      save_session(session);
      set_auth_session(session);
      form.reset();
      set_error_message('');
      await load_habits();
    } catch (error) {
      set_error_message(error.message || 'Unable to register');
    }
  }

  function handle_logout() {
    clear_session();
    app_state.habits = [];
    app_state.habit_logs_by_habit_id = {};
    set_auth_session(null);
    set_error_message('');
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
          habit_logs_by_habit_id: app_state.habit_logs_by_habit_id,
          month_date: app_state.selected_month,
          on_toggle_day: handle_toggle_day
        });
      });
    }

    const next_button = document.getElementById('next-month');
    if (next_button) {
      next_button.addEventListener('click', () => {
        app_state.selected_month = new Date(app_state.selected_month.getFullYear(), app_state.selected_month.getMonth() + 1, 1);
        render_calendar({
          habits: app_state.habits,
          habit_logs_by_habit_id: app_state.habit_logs_by_habit_id,
          month_date: app_state.selected_month,
          on_toggle_day: handle_toggle_day
        });
      });
    }

    document.getElementById('login-form')?.addEventListener('submit', handle_login_submit);
    document.getElementById('register-form')?.addEventListener('submit', handle_register_submit);
    document.getElementById('logout-button')?.addEventListener('click', handle_logout);
    document.getElementById('show-login')?.addEventListener('click', () => {
      app_state.auth_mode = 'login';
      render_auth_mode();
      set_error_message('');
    });
    document.getElementById('show-register')?.addEventListener('click', () => {
      app_state.auth_mode = 'register';
      render_auth_mode();
      set_error_message('');
    });
  }

  const saved_theme = localStorage.getItem('habit_tracker_theme') || 'light';
  apply_theme(saved_theme);
  attach_event_listeners();
  set_auth_session(get_session());
  load_habits();
})();
