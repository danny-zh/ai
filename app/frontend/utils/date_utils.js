(function (global, factory) {
  const api = factory();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
    return;
  }

  global.HabitTracker = global.HabitTracker || {};
  Object.assign(global.HabitTracker, api);
})(typeof window !== 'undefined' ? window : globalThis, function () {
  function get_days_in_month(year, month_index) {
    return new Date(year, month_index + 1, 0).getDate();
  }

  function format_date_key(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function get_month_label(date) {
    return new Intl.DateTimeFormat('en-US', {
      month: 'long',
      year: 'numeric'
    }).format(date);
  }

  function build_month_days(year, month_index) {
    const month_start = new Date(year, month_index, 1);
    const total_days = get_days_in_month(year, month_index);
    const leading_days = month_start.getDay();
    const total_cells = Math.ceil((leading_days + total_days) / 7) * 7;
    const days = [];

    for (let index = 0; index < total_cells; index += 1) {
      const day_offset = index - leading_days + 1;
      const date = new Date(year, month_index, day_offset);
      const date_key = format_date_key(date);

      days.push({
        date,
        date_key,
        day_number: date.getDate(),
        is_current_month: date.getMonth() === month_index,
        is_today: date_key === format_date_key(new Date())
      });
    }

    return days;
  }

  return {
    get_days_in_month,
    format_date_key,
    get_month_label,
    build_month_days
  };
});
