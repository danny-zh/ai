const { create_app_state, has_habit_log_on } = require('../src/app');

describe('app state helpers', () => {
  test('creates backend-shaped habit and log state', () => {
    const state = create_app_state();

    expect(state.habits).toEqual([]);
    expect(state.habit_logs_by_habit_id).toEqual({});
    expect(state.session).toBeNull();
    expect(state.auth_mode).toBe('login');
  });

  test('derives completion from backend-shaped habit logs', () => {
    const habit_logs_by_habit_id = {
      4: [{ id_habit: 4, id_user: 2, habit_duration: 60, log_date: '2026-09-04' }]
    };

    expect(has_habit_log_on(habit_logs_by_habit_id, 4, '2026-09-04')).toBe(true);
    expect(has_habit_log_on(habit_logs_by_habit_id, 4, '2026-09-05')).toBe(false);
    expect(has_habit_log_on(habit_logs_by_habit_id, 5, '2026-09-04')).toBe(false);
  });
});