const {
  clear_session,
  get_session,
  is_authenticated,
  save_session,
  storage_keys
} = require('../services/auth_session');

function create_storage() {
  const values = new Map();
  return {
    clear: jest.fn(() => values.clear()),
    getItem: jest.fn((key) => values.get(key) || null),
    removeItem: jest.fn((key) => values.delete(key)),
    setItem: jest.fn((key, value) => values.set(key, value))
  };
}

describe('auth_session', () => {
  const storage_owner = typeof window !== 'undefined' ? window : global;

  beforeEach(() => {
    if (!storage_owner.localStorage) {
      Object.defineProperty(storage_owner, 'localStorage', {
        configurable: true,
        value: create_storage()
      });
    }
    storage_owner.localStorage.clear?.();
  });

  afterEach(() => {
    storage_owner.localStorage.clear?.();
  });

  test('saves and reads a complete session', () => {
    save_session({ access_token: 'jwt', user_id: 8, username: 'sam' });

    expect(get_session()).toEqual({ access_token: 'jwt', user_id: 8, username: 'sam' });
    expect(is_authenticated()).toBe(true);
  });

  test('rejects incomplete sessions', () => {
    storage_owner.localStorage.setItem(storage_keys.access_token, 'jwt');
    storage_owner.localStorage.setItem(storage_keys.username, 'sam');

    expect(get_session()).toBeNull();
    expect(is_authenticated()).toBe(false);
  });

  test('clears stored session values', () => {
    save_session({ access_token: 'jwt', user_id: 8, username: 'sam' });
    clear_session();

    expect(get_session()).toBeNull();
    expect(storage_owner.localStorage.getItem(storage_keys.access_token)).toBeNull();
    expect(storage_owner.localStorage.getItem(storage_keys.user_id)).toBeNull();
    expect(storage_owner.localStorage.getItem(storage_keys.username)).toBeNull();
  });
});