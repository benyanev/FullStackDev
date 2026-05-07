import { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Collapse from '@mui/material/Collapse';
import Divider from '@mui/material/Divider';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';

function SinglePost({ title, email, body }) {
  const [expanded, setExpanded] = useState(false);

  // JSONPlaceholder bodies use '\n' to separate lines
  const lines = body.split('\n');
  const preview = lines.slice(0, 3).join('\n');
  const rest = lines.slice(3).join('\n');
  const hasMore = lines.length > 3;

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

        {/* First 3 lines (always visible) */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}
        >
          {preview}
        </Typography>

        {/* Remaining lines (collapsible) */}
        {hasMore && (
          <Collapse in={expanded} timeout={350}>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}
            >
              {rest}
            </Typography>
          </Collapse>
        )}
      </CardContent>

      {/* Read More / Show Less toggle */}
      {hasMore && (
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
