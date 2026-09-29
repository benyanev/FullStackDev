import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Avatar from '@mui/material/Avatar';
import Divider from '@mui/material/Divider';
import CircularProgress from '@mui/material/CircularProgress';
import { useAuth } from '../../context/AuthContext';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { createComment, fetchComments } from '../../services/comments.service';
import { suggestComment } from '../../services/ai.service';
import { getAvatarColor } from '../../utils/avatarColor';
import { timeAgo } from '../../utils/timeAgo';
import ModerationDialog from '../ModerationDialog';
import AgentBadge from '../AgentBadge';

/**
 * CommentSection — inline comment list with a text input for new comments
 * and a ✨ button that asks the AI to suggest a comment.
 *
 * @param {Object}   props
 * @param {number}   props.postId       - The post's ID.
 * @param {Function} props.onCountChange - Callback to update the parent's comment count.
 */
function CommentSection({ postId, onCountChange }) {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [body, setBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [moderationMessage, setModerationMessage] = useState('');
  const [suggesting, setSuggesting] = useState(false);

  const applyComments = useCallback((data) => {
    setComments(data.comments);
    onCountChange(data.count);
  }, [onCountChange]);

  // Initial load (same .then() pattern as PostActions / useAdminDashboard)
  useEffect(() => {
    fetchComments(postId)
      .then(applyComments)
      .catch(() => setError('Could not load comments.'))
      .finally(() => setLoading(false));
  }, [postId, applyComments]);

  // Ask the AI for a comment based on this post and its comments
  const handleSuggest = async () => {
    setSuggesting(true);
    setError('');
    try {
      const data = await suggestComment(postId);
      setBody(data.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setSuggesting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = body.trim();
    if (!trimmed || submitting) return;

    setSubmitting(true);
    setError('');
    try {
      await createComment(postId, trimmed);
      setBody('');
      applyComments(await fetchComments(postId));
    } catch (err) {
      // 422 = blocked as toxic: explain in a dialog and keep the text for editing
      if (err.status === 422) {
        setModerationMessage(err.message);
      } else {
        setError(err.message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 1.5 }}>
      <Divider sx={{ mb: 1.5 }} />

      {/* Comment list */}
      {comments.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, fontStyle: 'italic' }}>
          No comments yet. Be the first!
        </Typography>
      )}

      {comments.map((comment) => {
        const name = comment.authorName;
        const color = getAvatarColor(name);

        return (
          <Box key={comment.id} sx={{ display: 'flex', gap: 1, mb: 1.5 }}>
            <Avatar
              component={Link}
              to={`/profile/${comment.author_id}`}
              sx={{
                width: 28,
                height: 28,
                bgcolor: color,
                fontSize: 13,
                fontWeight: 700,
                textDecoration: 'none',
                flexShrink: 0,
                mt: 0.25,
              }}
            >
              {name[0].toUpperCase()}
            </Avatar>
            <Box sx={{ minWidth: 0 }}>
              <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.75 }}>
                <Typography
                  component={Link}
                  to={`/profile/${comment.author_id}`}
                  variant="caption"
                  sx={{
                    fontWeight: 700,
                    color: 'text.primary',
                    textDecoration: 'none',
                    '&:hover': { textDecoration: 'underline' },
                  }}
                >
                  {name}
                </Typography>
                {Boolean(comment.authorIsAgent) && <AgentBadge />}
                <Typography variant="caption" color="text.secondary">
                  {timeAgo(comment.created_at)}
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{
                  color: 'text.secondary',
                  lineHeight: 1.5,
                  overflowWrap: 'anywhere',
                }}
              >
                {comment.body}
              </Typography>
            </Box>
          </Box>
        );
      })}

      {/* New comment input */}
      {user && (
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ display: 'flex', gap: 1, mt: 1 }}
        >
          <TextField
            id={`comment-input-${postId}`}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Write a comment…"
            size="small"
            fullWidth
            multiline
            maxRows={3}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                fontSize: '0.85rem',
              },
            }}
          />
          <Tooltip title="Suggest a comment with AI">
            <span style={{ alignSelf: 'flex-end' }}>
              <IconButton
                id={`suggest-comment-btn-${postId}`}
                size="small"
                color="primary"
                onClick={handleSuggest}
                disabled={suggesting || submitting}
              >
                {suggesting ? <CircularProgress size={18} /> : <AutoAwesomeIcon fontSize="small" />}
              </IconButton>
            </span>
          </Tooltip>
          <Button
            type="submit"
            variant="contained"
            size="small"
            disabled={!body.trim() || submitting}
            sx={{
              textTransform: 'none',
              fontWeight: 600,
              borderRadius: 2,
              minWidth: 64,
              alignSelf: 'flex-end',
            }}
          >
            {submitting ? '…' : 'Post'}
          </Button>
        </Box>
      )}

      {error && (
        <Typography variant="caption" color="error" sx={{ display: 'block', mt: 0.5 }}>
          {error}
        </Typography>
      )}

      <ModerationDialog message={moderationMessage} onClose={() => setModerationMessage('')} />
    </Box>
  );
}

export default CommentSection;
