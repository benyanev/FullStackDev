import { useState, useEffect, useRef } from 'react';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Fade from '@mui/material/Fade';
import { fetchPosts, fetchUser } from '../services/api';
import SinglePost from './SinglePost';

const LIMIT = 10;

function Feed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const startRef = useRef(0);
  const hasFetched = useRef(false);

  const loadPosts = async () => {
    setLoading(true);
    try {
      const newPosts = await fetchPosts(startRef.current, LIMIT);

      // Attach the author email to each post
      const postsWithEmail = await Promise.all(
        newPosts.map(async (post) => {
          const user = await fetchUser(post.userId);
          return { ...post, email: user.email };
        })
      );

      setPosts((prev) => [...prev, ...postsWithEmail]);
      startRef.current += LIMIT;
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch the first batch on mount (guard against StrictMode double-fire)
  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      loadPosts();
    }
  }, []);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 4 }}>
      {/* Section title */}
      <Typography
        variant="h4"
        sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}
      >
        Latest Posts
      </Typography>

      <Grid container spacing={3}>
        {posts.map((post, index) => (
          <Fade
            key={post.id}
            in
            timeout={400 + (index % LIMIT) * 100}
          >
            <Grid size={{ xs: 12, sm: 6, md: 4 }}>
              <SinglePost
                title={post.title}
                email={post.email}
                body={post.body}
              />
            </Grid>
          </Fade>
        ))}
      </Grid>

      {/* Load More / Spinner */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        {loading ? (
          <CircularProgress size={40} thickness={4} />
        ) : (
          <Button
            variant="contained"
            onClick={loadPosts}
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
