const { build_month_days, format_date_key, get_month_label } = require('../utils/date_utils');

describe('date_utils', () => {
  test('build_month_days returns a grid covering the full month', () => {
    const days = build_month_days(2026, 7);

    expect(days.length).toBeGreaterThanOrEqual(35);
    expect(days[0].is_current_month).toBe(false);
    expect(days[days.length - 1].is_current_month).toBe(false);
    expect(days.some((day) => day.day_number === 1 && day.is_current_month)).toBe(true);
  });

  test('format_date_key uses yyyy-mm-dd format', () => {
    const date = new Date(2026, 7, 15);
    expect(format_date_key(date)).toBe('2026-08-15');
  });

  test('get_month_label formats as month year', () => {
    const date = new Date(2026, 7, 1);
    expect(get_month_label(date)).toBe('August 2026');
  });
});
