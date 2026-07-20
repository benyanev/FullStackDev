import { useState, useRef, useCallback, useEffect } from 'react';
import { fetchUsers } from '../../services/users.service';

const LIMIT = 10;

/**
 * Custom hook for the Users page.
 * Manages user list fetching with pagination and provides a loading-guarded
 * loadMore callback for the infinite scroll hook.
 *
 * @returns {{
 *   users: Array,
 *   loading: boolean,
 *   hasMore: boolean,
 *   loadMore: () => void,
 * }}
 */
export function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const startRef = useRef(0);
  const hasFetched = useRef(false);
  const loadingRef = useRef(false);

  const loadMore = useCallback(async () => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    try {
      const newUsers = await fetchUsers(startRef.current, LIMIT);
      setUsers((prev) => [...prev, ...newUsers]);
      startRef.current += LIMIT;
      setHasMore(newUsers.length === LIMIT);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  }, []);

  // Initial load on mount (with StrictMode guard)
  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      loadMore();
    }
  }, [loadMore]);

  return { users, loading, hasMore, loadMore };
}
