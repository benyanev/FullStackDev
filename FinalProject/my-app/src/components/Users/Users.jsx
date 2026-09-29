import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useInfiniteScroll } from '../../hooks/useInfiniteScroll';
import { useUsers } from './useUsers';
import Search from '../Search/Search';
import User from '../User/User';

/**
 * Users page — displays an infinite-scrolling list of user cards with an
 * autocomplete search bar. The search opens a dropdown to find
 * users by name; the grid always shows the full user list.
 */
function Users() {
  const { users, loading, hasMore, loadMore } = useUsers();
  const sentinelRef = useInfiniteScroll(loadMore, hasMore);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: { xs: 2, sm: 3 }, py: { xs: 2.5, sm: 4 } }}>
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
              bio={user.bio}
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
