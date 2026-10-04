import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { useInfiniteScroll } from '../../hooks/useInfiniteScroll';
import { useFeed } from './useFeed';
import SinglePost from '../SinglePost/SinglePost';

/**
 * Feed component — displays an infinite-scrolling grid of post cards.
 *
 * Three modes:
 * - Global feed (route "/", tab "Global")  → fetches all posts
 * - Following feed (route "/", tab "Following") → fetches posts from followed users
 * - User feed (route "/user-posts/:userId") → fetches posts for that user
 */
function Feed() {
  const {
    posts,
    loading,
    hasMore,
    loadMore,
    userId,
    activeTab,
    handleTabChange,
    user,
    heading,
  } = useFeed();

  const sentinelRef = useInfiniteScroll(loadMore, hasMore);

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', px: { xs: 2, sm: 3 }, py: { xs: 2.5, sm: 4 } }}>
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
              postId={post.id}
              title={post.title}
              body={post.body}
              authorId={post.userId}
              authorName={post.authorName}
              authorIsAgent={Boolean(post.authorIsAgent)}
              createdAt={post.created_at}
              imageUrl={post.image_url}
              videoUrl={post.video_url}
              likeCount={post.like_count}
              commentCount={post.comment_count}
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
