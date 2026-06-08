import { useState, useEffect, useRef, useCallback } from 'react';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { fetchUsers } from '../services/api';
import Search from './Search';
import User from './User';

const LIMIT = 10;

/**
 * Users page — displays an infinite-scrolling list of user cards with an
 * autocomplete search bar. The search opens a dropdown to find
 * users by name; the grid always shows the full user list.
 */
function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const startRef = useRef(0);
  const hasFetched = useRef(false);
  const loadingRef = useRef(false);

  // Sentinel ref for IntersectionObserver
  const sentinelRef = useRef(null);

  const loadUsers = useCallback(async () => {
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
      loadUsers();
    }
  }, []);

  // IntersectionObserver for infinite scroll
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loadingRef.current && hasMore) {
          loadUsers();
        }
      },
      { rootMargin: '200px' }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loadUsers]);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 4 }}>
      {/* Page title */}
      <Typography
        variant="h4"
        sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}
      >
        Users
      </Typography>

      {/* Autocomplete search bar — dropdown only, doesn't affect the grid */}
      <Search />

      {/* User cards grid */}
      <Grid container spacing={3}>
        {users.map((user) => (
          <Grid key={user.id} size={{ xs: 12, sm: 6 }}>
            <User
              id={user.id}
              name={user.name}
              email={user.email}
              followersCount={user.followers_count || 0}
              followingCount={user.following_count || 0}
            />
          </Grid>
        ))}
      </Grid>

      {/* Infinite scroll spinner */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 2 }}>
        {loading && <CircularProgress size={36} thickness={4} />}
      </Box>

      {/* Sentinel element — observed by IntersectionObserver to trigger next page load */}
      {hasMore && <div ref={sentinelRef} style={{ height: 1 }} />}

      {/* End of list message */}
      {!hasMore && users.length > 0 && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ textAlign: 'center', mt: 2, mb: 2, fontStyle: 'italic' }}
        >
          You've reached the end
        </Typography>
      )}
    </Box>
  );
}

export default Users;
