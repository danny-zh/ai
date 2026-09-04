(function (global, factory) {
  const api = factory();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  global.HabitTracker = global.HabitTracker || {};
  Object.assign(global.HabitTracker, api);
})(typeof window !== 'undefined' ? window : globalThis, function () {
  const week_days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  function render_calendar({ habits, habit_logs_by_habit_id = {}, month_date, on_toggle_day }) {
    const calendar_element = document.getElementById('calendar');

    if (!calendar_element) {
      return;
    }

    const year = month_date.getFullYear();
    const month_index = month_date.getMonth();
    const month_days = globalThis.HabitTracker.build_month_days(year, month_index);
    const heading = document.getElementById('current-month-label');
    if (heading) {
      heading.textContent = globalThis.HabitTracker.get_month_label(month_date);
    }

    if (!habits.length) {
      calendar_element.innerHTML = '<p class="empty-state">No habits yet. Add one to start tracking.</p>';
      return;
    }

    const table = document.createElement('table');
    table.className = 'calendar-table';

    const thead = document.createElement('thead');
    const head_row = document.createElement('tr');

    week_days.forEach((day_name) => {
      const th = document.createElement('th');
      th.textContent = day_name;
      head_row.appendChild(th);
    });

    thead.appendChild(head_row);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    const weeks = [];

    for (let index = 0; index < month_days.length; index += 7) {
      weeks.push(month_days.slice(index, index + 7));
    }

    weeks.forEach((week) => {
      const row = document.createElement('tr');

      week.forEach((day) => {
        const cell = document.createElement('td');
        const is_today = day.date_key === globalThis.HabitTracker.format_date_key(new Date());
        cell.className = 'day-cell';

        if (!day.is_current_month) {
          cell.classList.add('is-outside-month');
        }

        if (is_today) {
          cell.classList.add('is-today');
        }

        const day_number = document.createElement('div');
        day_number.className = 'day-number';
        day_number.textContent = day.day_number;
        cell.appendChild(day_number);

        const habit_stack = document.createElement('div');
        habit_stack.className = 'habit-stack';

        habits.forEach((habit) => {
          const toggle = document.createElement('button');
          const done = globalThis.HabitTracker.has_habit_log_on(habit_logs_by_habit_id, habit.id, day.date_key);
          toggle.type = 'button';
          toggle.className = 'mini-toggle';
          if (done) {
            toggle.classList.add('is-done');
            toggle.style.background = habit.color;
            toggle.style.borderColor = habit.color;
            toggle.style.boxShadow = `inset 0 0 0 1px ${habit.color}55`;
          } else {
            toggle.style.background = 'rgba(148, 163, 184, 0.14)';
            toggle.style.borderColor = 'var(--border)';
            toggle.style.boxShadow = 'none';
          }
          toggle.title = `${habit.name} on ${day.date_key}`;
          toggle.setAttribute('aria-label', `${habit.name} ${done ? 'completed' : 'not completed'} on ${day.date_key}`);
          toggle.addEventListener('click', () => on_toggle_day(habit.id, day.date_key));
          habit_stack.appendChild(toggle);
        });

        cell.appendChild(habit_stack);
        row.appendChild(cell);
      });

      tbody.appendChild(row);
    });

    table.appendChild(tbody);
    calendar_element.innerHTML = '';
    calendar_element.appendChild(table);
  }

  return {
    render_calendar,
    week_days
  };
});
