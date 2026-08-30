const { get_habits } = require('../services/habit_api');

describe('habit_api', () => {
  afterEach(() => {
    delete global.fetch;
  });

  test('returns a fallback list when the backend is unavailable', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Network unavailable'));

    const habits = await get_habits();

    expect(Array.isArray(habits)).toBe(true);
    expect(habits.length).toBeGreaterThan(0);
    expect(habits[0]).toHaveProperty('name');
    expect(habits[0]).toHaveProperty('entries');
  });
});
