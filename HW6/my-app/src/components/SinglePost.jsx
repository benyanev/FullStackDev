import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DOMPurify from 'dompurify';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';

const BACKEND_URL = 'http://localhost:5000';

/**
 * Format an ISO timestamp into a human-readable "time ago" string.
 * @param {string} isoString - ISO 8601 date string from the backend.
 * @returns {string} e.g. "just now", "5 minutes ago", "2 hours ago", "3 days ago"
 */
function timeAgo(isoString) {
  if (!isoString) return '';
  const now = Date.now();
  const then = new Date(isoString).getTime();
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days !== 1 ? 's' : ''} ago`;
  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks} week${weeks !== 1 ? 's' : ''} ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months} month${months !== 1 ? 's' : ''} ago`;
  const years = Math.floor(days / 365);
  return `${years} year${years !== 1 ? 's' : ''} ago`;
}

/**
 * Check if a string contains HTML tags (indicates rich text content from Tiptap).
 * @param {string} str
 * @returns {boolean}
 */
function containsHTML(str) {
  return /<[a-z][\s\S]*>/i.test(str);
}

/**
 * SinglePost — expandable post card.
 * Shows the author avatar, post title, optional image, and body.
 * Body can be plain text (clamped to 3 lines) or rich HTML from Tiptap.
 * A "Read More" button appears when the body overflows the clamp.
 *
 * @param {Object}  props
 * @param {string}  props.title     - Post title.
 * @param {string}  props.email     - Author email (used for avatar and label).
 * @param {string}  props.body      - Full post body (plain text or HTML).
 * @param {number}  props.authorId  - Author user ID (for profile link).
 * @param {string}  props.authorName - Author display name.
 * @param {string}  props.createdAt - ISO timestamp of when the post was created.
 * @param {string}  props.imageUrl  - Optional image URL for the post.
 */
function SinglePost({ title, email, body, authorId, authorName, createdAt, imageUrl }) {
  const [expanded, setExpanded] = useState(false);
  const [clamped, setClamped] = useState(false);
  const bodyRef = useRef(null);

  const isHTML = containsHTML(body);

  // After render, check if the text is actually overflowing the 3-line clamp.
  // If scrollHeight > clientHeight the content is taller than the visible area.
  useEffect(() => {
    const el = bodyRef.current;
    if (el) {
      setClamped(el.scrollHeight > el.clientHeight + 1);
    }
  }, [body, expanded]);

  // Generate a consistent color from the email string
  const avatarColor = `hsl(${[...email].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360}, 55%, 50%)`;

  // Display name: prefer authorName, fall back to email
  const displayName = authorName || email;

  // Build the full image URL if the imageUrl is a relative path
  const fullImageUrl = imageUrl
    ? imageUrl.startsWith('http')
      ? imageUrl
      : `${BACKEND_URL}${imageUrl}`
    : '';

  // Sanitize HTML content for XSS prevention
  const sanitizedBody = isHTML ? DOMPurify.sanitize(body) : '';

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
      {/* Post image (if attached) */}
      {fullImageUrl && (
        <CardMedia
          component="img"
          image={fullImageUrl}
          alt={title}
          sx={{
            height: 200,
            objectFit: 'cover',
          }}
        />
      )}

      <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
        {/* Author row */}
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
            {/* Timestamp */}
            {createdAt && (
              <Typography variant="caption" color="text.secondary">
                {timeAgo(createdAt)}
              </Typography>
            )}
          </Box>
        </Box>

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

        {/* Post body — rich HTML or plain text, clamped to 3 lines unless expanded */}
        {isHTML ? (
          <Box
            ref={bodyRef}
            sx={{
              lineHeight: 1.7,
              overflowWrap: 'anywhere',
              fontSize: '0.875rem',
              color: 'text.secondary',
              ...(!expanded
                ? {
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }
                : {}),
              '& p': { m: 0, mb: 0.5 },
              '& ul, & ol': { pl: 3, my: 0.5 },
              '& blockquote': {
                borderLeft: '3px solid',
                borderColor: 'divider',
                pl: 2,
                ml: 0,
                fontStyle: 'italic',
              },
              '& code': {
                bgcolor: 'action.hover',
                borderRadius: 1,
                px: 0.5,
                fontFamily: 'monospace',
                fontSize: '0.85em',
              },
              '& pre': {
                bgcolor: 'grey.900',
                color: 'grey.100',
                borderRadius: 2,
                p: 1.5,
                fontFamily: 'monospace',
                fontSize: '0.85em',
                overflowX: 'auto',
              },
            }}
            dangerouslySetInnerHTML={{ __html: sanitizedBody }}
          />
        ) : (
          <Typography
            ref={bodyRef}
            variant="body2"
            color="text.secondary"
            sx={{
              whiteSpace: 'pre-line',
              lineHeight: 1.7,
              overflowWrap: 'anywhere',
              wordBreak: 'break-all',
              ...(!expanded
                ? {
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }
                : {}),
            }}
          >
            {body}
          </Typography>
        )}
      </CardContent>

      {/* Read More / Show Less toggle — shown only when text actually overflows */}
      {(clamped || expanded) && (
        <CardActions sx={{ px: 2.5, pb: 2 }}>
          <Button
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{
              textTransform: 'none',
              fontWeight: 600,
              borderRadius: 2,
            }}
          >
            {expanded ? 'Show Less' : 'Read More'}
          </Button>
        </CardActions>
      )}
    </Card>
  );
}

export default SinglePost;
