import { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, signupUser, logoutUser, fetchCurrentUser } from '../services/api';

/**
 * AuthContext provides user authentication state across the app.
 *
 * Session management is fully server-side via HttpOnly cookies.
 * No tokens or credentials are stored in localStorage.
 *
 * Exposes:
 * - user      — the logged-in user object (or null)
 * - loading   — true while the initial session check is in progress
 * - login()   — authenticates with the backend
 * - signup()  — registers with the backend
 * - logout()  — destroys the server session and clears state
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, check if an existing session cookie is still valid
  useEffect(() => {
    fetchCurrentUser()
      .then((userData) => setUser(userData))
      .finally(() => setLoading(false));
  }, []);

  /**
   * Log in with real credentials via the backend.
   * The server sets the session cookie automatically.
   * @param {string} email
   * @param {string} password
   * @throws {Error} If credentials are invalid.
   */
  const login = async (email, password) => {
    const data = await loginUser(email, password);
    setUser(data.user);
  };

  /**
   * Register a new account via the backend.
   * The server sets the session cookie automatically.
   * @param {string} name
   * @param {string} email
   * @param {string} password
   * @throws {Error} If registration fails (e.g. email taken).
   */
  const signup = async (name, email, password) => {
    const data = await signupUser(name, email, password);
    setUser(data.user);
  };

  /** Destroy the server session and clear local state. */
  const logout = async () => {
    await logoutUser();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to access auth state from any component.
 * Usage: const { user, loading, login, signup, logout } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
