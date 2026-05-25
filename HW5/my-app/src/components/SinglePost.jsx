import { useState, useRef, useEffect } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';

/**
 * SinglePost — expandable post card.
 * Shows the author avatar, post title, and body clamped to 3 visible lines.
 * A "Read More" button appears when the body overflows the clamp.
 *
 * @param {Object}  props
 * @param {string}  props.title - Post title.
 * @param {string}  props.email - Author email (used for avatar and label).
 * @param {string}  props.body  - Full post body text.
 */
function SinglePost({ title, email, body }) {
  const [expanded, setExpanded] = useState(false);
  const [clamped, setClamped] = useState(false);
  const bodyRef = useRef(null);

  // After render, check if the text is actually overflowing the 3-line clamp.
  // If scrollHeight > clientHeight the content is taller than the visible area.
  useEffect(() => {
    const el = bodyRef.current;
    if (el) {
      setClamped(el.scrollHeight > el.clientHeight + 1);
    }
  }, [body]);

  // Generate a consistent color from the email string
  const avatarColor = `hsl(${[...email].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360}, 55%, 50%)`;

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
      <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
        {/* Author row */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
          <Avatar
            sx={{
              width: 36,
              height: 36,
              bgcolor: avatarColor,
              fontSize: 16,
              fontWeight: 700,
              mr: 1.5,
            }}
          >
            {email[0].toUpperCase()}
          </Avatar>
          <Typography variant="body2" color="text.secondary">
            {email}
          </Typography>
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

        {/* Post body — always clamped to 3 lines unless expanded */}
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

