import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { fetchPosts, fetchUser, fetchUserPosts, fetchFollowingPosts } from '../services/api';
import { useAuth } from '../context/AuthContext';
import SinglePost from './SinglePost';

const LIMIT = 10;

/**
 * Feed component — displays an infinite-scrolling grid of post cards.
 *
 * Three modes:
 * - Global feed (route "/", tab "Global")  → fetches all posts via fetchPosts
 * - Following feed (route "/", tab "Following") → fetches posts from followed users
 * - User feed (route "/user-posts/:userId") → fetches posts for that user via fetchUserPosts
 */
function Feed() {
  const { userId } = useParams(); // undefined on "/" , a string on "/user-posts/:userId"
  const { user } = useAuth();

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userName, setUserName] = useState('');
  const [activeTab, setActiveTab] = useState(0); // 0 = Global, 1 = Following
  const [hasMore, setHasMore] = useState(true);
  const startRef = useRef(0);
  const hasFetched = useRef(false);
  // Track which userId was last loaded so we can reset when it changes
  const prevUserIdRef = useRef(userId);

  // Sentinel ref for IntersectionObserver
  const sentinelRef = useRef(null);
  // Keep a ref to loading to avoid stale closures in the observer callback
  const loadingRef = useRef(false);

  const loadPosts = useCallback(async (reset = false, tab = activeTab) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    try {
      const start = reset ? 0 : startRef.current;

      let newPosts;
      if (userId) {
        // User-specific feed (route /user-posts/:userId)
        newPosts = await fetchUserPosts(userId, start, LIMIT);
      } else if (tab === 1 && user) {
        // Following feed tab
        newPosts = await fetchFollowingPosts(start, LIMIT);
      } else {
        // Global feed (default)
        newPosts = await fetchPosts(start, LIMIT);
      }

      if (reset) {
        setPosts(newPosts);
        startRef.current = LIMIT;
      } else {
        setPosts((prev) => [...prev, ...newPosts]);
        startRef.current += LIMIT;
      }

      // If we got fewer than LIMIT results, there are no more posts
      setHasMore(newPosts.length === LIMIT);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  }, [userId, user, activeTab]);

  // Fetch on mount and reset when userId changes
  useEffect(() => {
    // If the userId changed (e.g. navigated from "/" to "/user-posts/3"), reset
    if (prevUserIdRef.current !== userId) {
      prevUserIdRef.current = userId;
      hasFetched.current = false;
      startRef.current = 0;
      setHasMore(true);
    }

    if (!hasFetched.current) {
      hasFetched.current = true;

      // If viewing a specific user's posts, also fetch their name for the heading
      if (userId) {
        fetchUser(userId).then((u) => setUserName(u.name));
      } else {
        setUserName('');
      }

      loadPosts(true);
    }
  }, [userId]);

  // IntersectionObserver for infinite scroll
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loadingRef.current && hasMore) {
          loadPosts(false);
        }
      },
      { rootMargin: '200px' }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loadPosts]);

  // Handle tab change
  const handleTabChange = (_event, newValue) => {
    setActiveTab(newValue);
    startRef.current = 0;
    setPosts([]);
    setHasMore(true);
    // We need to pass the new tab value directly since state hasn't updated yet
    loadPosts(true, newValue);
  };

  // Heading text
  const heading = userId
    ? `Posts by ${userName || '...'}`
    : activeTab === 1
      ? 'Following Feed'
      : 'Latest Posts';

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: 3, py: 4 }}>
      {/* Tabs — only shown on the home feed (not on /user-posts/:userId) and only when logged in */}
      {!userId && user && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            mb: 3,
          }}
        >
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            sx={{
              minHeight: 44,
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                minHeight: 44,
                px: 3,
              },
              '& .MuiTabs-indicator': {
                height: 3,
                borderRadius: '3px 3px 0 0',
                background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
              },
            }}
          >
            <Tab label="Global" />
            <Tab label="Following" />
          </Tabs>
        </Box>
      )}

      {/* Section title */}
      <Typography
        variant="h4"
        sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}
      >
        {heading}
      </Typography>

      {/* Empty state for the Following tab */}
      {!loading && posts.length === 0 && activeTab === 1 && !userId && (
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ textAlign: 'center', mt: 4 }}
        >
          No posts yet. Follow some users to see their posts here!
        </Typography>
      )}

      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid key={post.id} size={{ xs: 12, sm: 6, md: 4 }}>
            <SinglePost
              title={post.title}
              email={post.email}
              body={post.body}
              authorId={post.userId}
              authorName={post.authorName}
              createdAt={post.created_at}
              imageUrl={post.image_url}
            />
          </Grid>
        ))}
      </Grid>

      {/* Infinite scroll sentinel + spinner */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 2 }}>
        {loading && <CircularProgress size={36} thickness={4} />}
      </Box>

      {/* Sentinel element — observed by IntersectionObserver to trigger next page load */}
      {hasMore && <div ref={sentinelRef} style={{ height: 1 }} />}

      {/* End of feed message */}
      {!hasMore && posts.length > 0 && (
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

export default Feed;
