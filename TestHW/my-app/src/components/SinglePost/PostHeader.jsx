import { Link } from 'react-router-dom';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { timeAgo } from '../../utils/timeAgo';

/**
 * PostHeader — displays the author avatar, name (linked to profile), and timestamp.
 *
 * @param {Object}  props
 * @param {number}  props.authorId    - Author user ID (for profile link).
 * @param {string}  props.displayName - Author display name.
 * @param {string}  props.avatarColor - HSL color for the avatar background.
 * @param {string}  props.createdAt   - ISO timestamp of when the post was created.
 */
function PostHeader({ authorId, displayName, avatarColor, createdAt }) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
      <Avatar
        component={authorId ? Link : 'div'}
        to={authorId ? `/profile/${authorId}` : undefined}
        sx={{
          width: 36,
          height: 36,
          bgcolor: avatarColor,
          fontSize: 16,
          fontWeight: 700,
          mr: 1.5,
          textDecoration: 'none',
          cursor: authorId ? 'pointer' : 'default',
        }}
      >
        {displayName[0].toUpperCase()}
      </Avatar>
      <Box sx={{ minWidth: 0 }}>
        <Typography
          component={authorId ? Link : 'span'}
          to={authorId ? `/profile/${authorId}` : undefined}
          variant="body2"
          sx={{
            fontWeight: 600,
            color: 'text.primary',
            textDecoration: 'none',
            display: 'block',
            '&:hover': authorId ? { textDecoration: 'underline' } : {},
          }}
        >
          {displayName}
        </Typography>
        {createdAt && (
          <Typography variant="caption" color="text.secondary">
            {timeAgo(createdAt)}
          </Typography>
        )}
      </Box>
    </Box>
  );
}

export default PostHeader;
