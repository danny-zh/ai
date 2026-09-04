const {
  create_habit,
  delete_habit_log,
  get_habit_logs,
  get_habits,
  upsert_habit_log
} = require('../services/habit_api');

function mock_json_response(payload, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: jest.fn().mockResolvedValue(payload)
  });
}

describe('habit_api', () => {
  const session = { access_token: 'token-123', user_id: 7, username: 'danny' };

  afterEach(() => {
    delete global.fetch;
  });

  test('gets backend-shaped habits for the authenticated user', async () => {
    const backend_habits = [{ id: 12, name: 'Read', color: '#10b981', description: null, id_user: 7 }];
    global.fetch = jest.fn().mockReturnValue(mock_json_response(backend_habits));

    const habits = await get_habits(session.user_id, session);

    expect(habits).toEqual(backend_habits);
    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8001/users/7/habits', {
      headers: {
        Authorization: 'Bearer token-123',
        'Content-Type': 'application/json'
      }
    });
  });

  test('creates a backend-shaped habit payload without entries', async () => {
    const created_habit = { id: 14, name: 'Workout', color: '#4f46e5', description: 'Lift', id_user: 7 };
    global.fetch = jest.fn().mockReturnValue(mock_json_response(created_habit, 201));

    const habit = await create_habit(session.user_id, { name: 'Workout', color: '#4f46e5', description: 'Lift' }, session);

    expect(habit).toEqual(created_habit);
    expect(JSON.parse(global.fetch.mock.calls[0][1].body)).toEqual({
      name: 'Workout',
      color: '#4f46e5',
      description: 'Lift'
    });
  });

  test('gets and changes backend-shaped habit logs', async () => {
    const logs = [{ id_habit: 14, id_user: 7, habit_duration: 60, log_date: '2026-09-04' }];
    global.fetch = jest
      .fn()
      .mockReturnValueOnce(mock_json_response(logs))
      .mockReturnValueOnce(mock_json_response(logs[0], 201))
      .mockReturnValueOnce(mock_json_response(null, 204));

    await expect(get_habit_logs(14, session)).resolves.toEqual(logs);
    await expect(upsert_habit_log(14, '2026-09-04', session)).resolves.toEqual(logs[0]);
    await expect(delete_habit_log(14, '2026-09-04', session)).resolves.toBe(true);

    expect(global.fetch.mock.calls[0][0]).toBe('http://localhost:8001/habits/14/logs');
    expect(global.fetch.mock.calls[1][0]).toBe('http://localhost:8001/habits/14/logs');
    expect(JSON.parse(global.fetch.mock.calls[1][1].body)).toEqual({ log_date: '2026-09-04', habit_duration: 60 });
    expect(global.fetch.mock.calls[2][0]).toBe('http://localhost:8001/habits/14/logs/2026-09-04');
  });

  test('throws backend detail instead of returning fallback data', async () => {
    global.fetch = jest.fn().mockReturnValue(mock_json_response({ detail: 'Not authenticated' }, 401));

    await expect(get_habits(session.user_id, session)).rejects.toThrow('Not authenticated');
  });
});
