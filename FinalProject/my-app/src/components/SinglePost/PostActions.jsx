import { useState, useEffect, useCallback } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutlined';
import FlagOutlinedIcon from '@mui/icons-material/FlagOutlined';
import Tooltip from '@mui/material/Tooltip';
import { useAuth } from '../../context/AuthContext';
import { toggleLike, fetchPostLikes } from '../../services/likes.service';
import ReportDialog from './ReportDialog';

/**
 * PostActions — like button with count, comment toggle button, and a
 * report (flag) button shown to logged-in users on other people's posts.
 *
 * @param {Object}   props
 * @param {number}   props.postId        - The post's ID.
 * @param {number}   props.authorId      - The post author's user ID.
 * @param {number}   props.initialLikeCount - Like count from the feed query.
 * @param {number}   props.commentCount  - Number of comments to display.
 * @param {boolean}  props.showComments  - Whether the comment section is open.
 * @param {Function} props.onToggleComments - Callback to toggle comment section.
 */
function PostActions({
  postId, authorId, initialLikeCount = 0, commentCount, showComments, onToggleComments,
}) {
  const { user } = useAuth();
  const userId = user?.id;
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(initialLikeCount);
  const [reportOpen, setReportOpen] = useState(false);

  const canReport = user && user.id !== authorId;

  // Logged-in users: ask whether *I* liked this post (the count comes with
  // the feed). Visitors can't like, so they skip this request.
  useEffect(() => {
    if (!userId) return;
    fetchPostLikes(postId)
      .then((data) => {
        setLiked(data.liked);
        setLikeCount(data.likeCount);
      })
      .catch(() => { });
  }, [postId, userId]);

  const handleLike = useCallback(async () => {
    if (!user) return;
    try {
      const data = await toggleLike(postId);
      setLiked(data.liked);
      setLikeCount(data.likeCount);
    } catch (err) {
      console.error('Like failed:', err);
    }
  }, [postId, user]);

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1.5 }}>
      {/* Like button */}
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <IconButton
          id={`like-btn-${postId}`}
          aria-label={liked ? 'Unlike' : 'Like'}
          size="small"
          onClick={handleLike}
          disabled={!user}
          sx={{
            color: liked ? '#e91e63' : 'text.secondary',
            transition: 'transform 0.2s ease',
            '&:hover': { transform: 'scale(1.15)' },
          }}
        >
          {liked ? <FavoriteIcon fontSize="small" /> : <FavoriteBorderIcon fontSize="small" />}
        </IconButton>
        <Typography variant="caption" color="text.secondary" sx={{ minWidth: 16 }}>
          {likeCount > 0 ? likeCount : ''}
        </Typography>
      </Box>

      {/* Comment toggle button */}
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <IconButton
          id={`comment-btn-${postId}`}
          aria-label="Comments"
          size="small"
          onClick={onToggleComments}
          sx={{
            color: showComments ? 'primary.main' : 'text.secondary',
            transition: 'transform 0.2s ease',
            '&:hover': { transform: 'scale(1.15)' },
          }}
        >
          <ChatBubbleOutlineIcon fontSize="small" />
        </IconButton>
        <Typography variant="caption" color="text.secondary" sx={{ minWidth: 16 }}>
          {commentCount > 0 ? commentCount : ''}
        </Typography>
      </Box>

      {/* Report button — pushed to the right */}
      {canReport && (
        <>
          <Tooltip title="Report post">
            <IconButton
              id={`report-btn-${postId}`}
              size="small"
              onClick={() => setReportOpen(true)}
              sx={{ ml: 'auto', color: 'text.secondary', '&:hover': { color: 'error.main' } }}
            >
              <FlagOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <ReportDialog postId={postId} open={reportOpen} onClose={() => setReportOpen(false)} />
        </>
      )}
    </Box>
  );
}

export default PostActions;
