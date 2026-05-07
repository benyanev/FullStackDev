import { useState, useEffect, useRef } from 'react';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { fetchUsers } from '../services/api';
import Search from './Search';
import User from './User';

const LIMIT = 10;

/**
 * Users page — displays a paginated list of user cards with an
 * autocomplete search bar. The search opens a dropdown to find
 * users by email; the grid always shows the full user list.
 */
function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const startRef = useRef(0);
  const hasFetched = useRef(false);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const newUsers = await fetchUsers(startRef.current, LIMIT);
      setUsers((prev) => [...prev, ...newUsers]);
      startRef.current += LIMIT;
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial load on mount (with StrictMode guard)
  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      loadUsers();
    }
  }, []);

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
            />
          </Grid>
        ))}
      </Grid>

      {/* Load More / Spinner */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        {loading ? (
          <CircularProgress size={40} thickness={4} />
        ) : (
          <Button
            variant="contained"
            onClick={loadUsers}
            sx={{
              borderRadius: 3,
              px: 4,
              py: 1.2,
              textTransform: 'none',
              fontWeight: 600,
              fontSize: '1rem',
              background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'scale(1.04)',
                boxShadow: '0 6px 20px rgba(45, 27, 105, 0.35)',
                background: 'linear-gradient(135deg, #24476f 0%, #371f7d 100%)',
              },
            }}
          >
            Load More
          </Button>
        )}
      </Box>
    </Box>
  );
}

export default Users;
