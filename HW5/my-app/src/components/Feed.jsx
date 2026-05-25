import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { fetchPosts, fetchUser, fetchUserPosts } from '../services/api';
import SinglePost from './SinglePost';

const LIMIT = 10;

/**
 * Feed component — displays a paginated grid of post cards.
 *
 * Two modes:
 * - Global feed (route "/")       → fetches all posts via fetchPosts
 * - User feed (route "/user-posts/:userId") → fetches posts for that user via fetchUserPosts
 */
function Feed() {
  const { userId } = useParams(); // undefined on "/" , a string on "/user-posts/:userId"

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userName, setUserName] = useState('');
  const startRef = useRef(0);
  const hasFetched = useRef(false);
  // Track which userId was last loaded so we can reset when it changes
  const prevUserIdRef = useRef(userId);

  const loadPosts = async (reset = false) => {
    setLoading(true);
    try {
      const start = reset ? 0 : startRef.current;

      // Backend returns posts with email already included (JOIN)
      const newPosts = userId
        ? await fetchUserPosts(userId, start, LIMIT)
        : await fetchPosts(start, LIMIT);

      if (reset) {
        setPosts(newPosts);
        startRef.current = LIMIT;
      } else {
        setPosts((prev) => [...prev, ...newPosts]);
        startRef.current += LIMIT;
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount and reset when userId changes
  useEffect(() => {
    // If the userId changed (e.g. navigated from "/" to "/user-posts/3"), reset
    if (prevUserIdRef.current !== userId) {
      prevUserIdRef.current = userId;
      hasFetched.current = false;
      startRef.current = 0;
    }

    if (!hasFetched.current) {
      hasFetched.current = true;

      // If viewing a specific user's posts, also fetch their name for the heading
      if (userId) {
        fetchUser(userId).then((user) => setUserName(user.name));
      } else {
        setUserName('');
      }

      loadPosts(true);
    }
  }, [userId]);

  // Heading text
  const heading = userId
    ? `Posts by ${userName || '...'}`
    : 'Latest Posts';

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 4 }}>
      {/* Section title */}
      <Typography
        variant="h4"
        sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}
      >
        {heading}
      </Typography>

      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid key={post.id} size={{ xs: 12, sm: 6, md: 4 }}>
            <SinglePost
              title={post.title}
              email={post.email}
              body={post.body}
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
            onClick={() => loadPosts(false)}
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

export default Feed;
