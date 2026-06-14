import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import { getAvatarColor } from '../../utils/avatarColor';
import PostHeader from './PostHeader';
import PostBody from './PostBody';

const BACKEND_URL = 'http://localhost:5000';

/**
 * SinglePost — expandable post card.
 * Shows the author avatar, post title, optional image, and body.
 *
 * @param {Object}  props
 * @param {string}  props.title      - Post title.
 * @param {string}  props.email      - Author email (used for avatar and label).
 * @param {string}  props.body       - Full post body (plain text or HTML).
 * @param {number}  props.authorId   - Author user ID (for profile link).
 * @param {string}  props.authorName - Author display name.
 * @param {string}  props.createdAt  - ISO timestamp of when the post was created.
 * @param {string}  props.imageUrl   - Optional image URL for the post.
 */
function SinglePost({ title, email, body, authorId, authorName, createdAt, imageUrl }) {
  const displayName = authorName || email;
  const avatarColor = getAvatarColor(displayName);

  // Build the full image URL if the imageUrl is a relative path
  const fullImageUrl = imageUrl
    ? imageUrl.startsWith('http')
      ? imageUrl
      : `${BACKEND_URL}${imageUrl}`
    : '';

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
          sx={{ height: 200, objectFit: 'cover' }}
        />
      )}

      <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
        <PostHeader
          authorId={authorId}
          displayName={displayName}
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
      </CardContent>
    </Card>
  );
}

export default SinglePost;
