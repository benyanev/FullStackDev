import { useState, useRef, useEffect } from 'react';
import DOMPurify from 'dompurify';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import { containsHTML } from '../../utils/timeAgo';

/**
 * PostBody — renders post content as either sanitized rich HTML or plain text.
 * Clamps the content to 3 lines, with a "Read More / Show Less" toggle
 * that appears only when the content actually overflows.
 *
 * @param {Object} props
 * @param {string} props.body - Full post body (plain text or HTML from Tiptap).
 */
function PostBody({ body }) {
  const [expanded, setExpanded] = useState(false);
  const [clamped, setClamped] = useState(false);
  const bodyRef = useRef(null);

  const isHTML = containsHTML(body);

  // After render, check if the text is actually overflowing the 3-line clamp.
  useEffect(() => {
    const el = bodyRef.current;
    if (el) {
      setClamped(el.scrollHeight > el.clientHeight + 1);
    }
  }, [body, expanded]);

  const clampStyles = !expanded
    ? {
        display: '-webkit-box',
        WebkitLineClamp: 3,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
      }
    : {};

  // Sanitize HTML content for XSS prevention
  const sanitizedBody = isHTML ? DOMPurify.sanitize(body) : '';

  return (
    <>
      {isHTML ? (
        <Box
          ref={bodyRef}
          sx={{
            lineHeight: 1.7,
            overflowWrap: 'anywhere',
            fontSize: '0.875rem',
            color: 'text.secondary',
            ...clampStyles,
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
            ...clampStyles,
          }}
        >
          {body}
        </Typography>
      )}

      {/* Read More / Show Less toggle — shown only when text actually overflows */}
      {(clamped || expanded) && (
        <CardActions sx={{ px: 0, pb: 0, pt: 1 }}>
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
    </>
  );
}

export default PostBody;
