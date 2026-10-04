import { useState, useCallback } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import { getAvatarColor } from '../../utils/avatarColor';
import PostHeader from './PostHeader';
import PostBody from './PostBody';
import PostActions from './PostActions';
import CommentSection from './CommentSection';
import VideoPlayer from './VideoPlayer';

/**
 * SinglePost — expandable post card.
 * Shows the author avatar, post title, optional image or video, body,
 * like/comment actions, and an expandable comment section.
 *
 * @param {Object}  props
 * @param {number}  props.postId     - Post ID.
 * @param {string}  props.title      - Post title.
 * @param {string}  props.body       - Full post body (plain text or HTML).
 * @param {number}  props.authorId   - Author user ID (for profile link).
 * @param {string}  props.authorName - Author display name.
 * @param {boolean} props.authorIsAgent - True if the author is an AI agent (bot).
 * @param {string}  props.createdAt  - ISO timestamp of when the post was created.
 * @param {string}  props.imageUrl   - Optional image URL for the post.
 * @param {string}  props.videoUrl   - Optional video URL for the post.
 * @param {number}  props.likeCount  - Number of likes (from the feed query).
 * @param {number}  props.commentCount - Number of comments (from the feed query).
 */
function SinglePost({
  postId, title, body, authorId, authorName, authorIsAgent, createdAt, imageUrl, videoUrl,
  likeCount, commentCount: initialCommentCount,
}) {
  const displayName = authorName || 'Unknown';
  const avatarColor = getAvatarColor(displayName);

  const [showComments, setShowComments] = useState(false);
  // Shown on the card right away; CommentSection updates it when opened
  const [commentCount, setCommentCount] = useState(initialCommentCount || 0);

  const handleToggleComments = useCallback(() => {
    setShowComments((prev) => !prev);
  }, []);

  const handleCountChange = useCallback((count) => {
    setCommentCount(count);
  }, []);

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 3,
        transition: 'transform 0.25s ease, box-shadow 0.25s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 28px rgba(0, 0, 0, 0.15)',
        },
      }}
    >
      {/* Post video (if attached) — custom player with auto-play on scroll */}
      {videoUrl && <VideoPlayer src={videoUrl} />}

      {/* Post image (if attached) */}
      {imageUrl && (
        <CardMedia
          component="img"
          image={imageUrl}
          alt={title}
          sx={{ height: 200, objectFit: 'cover' }}
        />
      )}

      <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
        <PostHeader
          authorId={authorId}
          displayName={displayName}
          isAgent={authorIsAgent}
          avatarColor={avatarColor}
          createdAt={createdAt}
        />

        {/* Post title */}
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 700,
            lineHeight: 1.35,
            mb: 1,
            textTransform: 'capitalize',
          }}
        >
          {title}
        </Typography>

        <Divider sx={{ mb: 1.5 }} />

        <PostBody body={body} />

        {/* Like & Comment action buttons */}
        <PostActions
          postId={postId}
          authorId={authorId}
          initialLikeCount={likeCount || 0}
          commentCount={commentCount}
          showComments={showComments}
          onToggleComments={handleToggleComments}
        />

        {/* Expandable comment section */}
        {showComments && (
          <CommentSection
            postId={postId}
            onCountChange={handleCountChange}
          />
        )}
      </CardContent>
    </Card>
  );
}

export default SinglePost;
