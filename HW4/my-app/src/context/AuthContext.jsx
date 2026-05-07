import { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, signupUser } from '../services/api';

/**
 * AuthContext provides user authentication state across the app.
 *
 * Exposes:
 * - user      — the logged-in user object (or null)
 * - token     — the JWT token string (or null)
 * - login()   — authenticates with the backend, stores JWT
 * - signup()  — registers with the backend, stores JWT
 * - logout()  — clears user and token from state and localStorage
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  // On mount, restore session from localStorage if a token exists
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
  }, []);

  /**
   * Log in with real credentials via the backend.
   * @param {string} email
   * @param {string} password
   * @throws {Error} If credentials are invalid.
   */
  const login = async (email, password) => {
    const data = await loginUser(email, password);
    setToken(data.token);
    setUser(data.user);
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  };

  /**
   * Register a new account via the backend.
   * @param {string} name
   * @param {string} email
   * @param {string} password
   * @throws {Error} If registration fails (e.g. email taken).
   */
  const signup = async (name, email, password) => {
    const data = await signupUser(name, email, password);
    setToken(data.token);
    setUser(data.user);
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
  };

  /** Clear auth state and remove the persisted session from localStorage. */
  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to access auth state from any component.
 * Usage: const { user, token, login, signup, logout } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
