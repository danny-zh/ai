const { login_user, register_user } = require('../services/auth_api');

function mock_json_response(payload, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: jest.fn().mockResolvedValue(payload)
  });
}

describe('auth_api', () => {
  afterEach(() => {
    delete global.fetch;
  });

  test('registers a user with backend request shape', async () => {
    const user = { id: 3, username: 'alex', email: 'alex@example.com' };
    global.fetch = jest.fn().mockReturnValue(mock_json_response(user, 201));

    await expect(register_user('alex', 'alex@example.com', 'password123')).resolves.toEqual(user);

    expect(global.fetch).toHaveBeenCalledWith('http://localhost:8001/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username: 'alex', email: 'alex@example.com', password: 'password123' }),
      headers: {
        'Content-Type': 'application/json'
      }
    });
  });

  test('logs in and returns the token response', async () => {
    const session = { access_token: 'jwt', token_type: 'bearer', user_id: 3, username: 'alex' };
    global.fetch = jest.fn().mockReturnValue(mock_json_response(session));

    await expect(login_user('alex', 'password123')).resolves.toEqual(session);
  });

  test('throws backend auth errors', async () => {
    global.fetch = jest.fn().mockReturnValue(mock_json_response({ detail: 'Invalid credentials' }, 401));

    await expect(login_user('alex', 'wrong')).rejects.toThrow('Invalid credentials');
  });
});