import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import { Link } from 'react-router-dom';

/**
 * Displays a single user's information in a card.
 *
 * @param {Object} props
 * @param {number} props.id       - User ID (used for the "View Posts" link).
 * @param {string} props.name     - User's full name.
 * @param {string} props.email    - User's email address.
 */
function User({ id, name, email }) {
  // Generate a consistent avatar color from the user's name
  const avatarColor = `hsl(${[...name].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360}, 55%, 50%)`;

  return (
    <Card
      sx={{
        height: '100%',
        minHeight: 180,
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
        {/* Avatar + Name */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
          <Avatar
            sx={{
              width: 44,
              height: 44,
              bgcolor: avatarColor,
              fontSize: 18,
              fontWeight: 700,
              mr: 1.5,
            }}
          >
            {name[0].toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.3 }}>
              {name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {email}
            </Typography>
          </Box>
        </Box>
      </CardContent>

      {/* View Posts button — links to /user-posts/:userId */}
      <CardActions sx={{ px: 2.5, pb: 2 }}>
        <Button
          component={Link}
          to={`/user-posts/${id}`}
          size="small"
          variant="outlined"
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            borderRadius: 2,
          }}
        >
          View Posts
        </Button>
      </CardActions>
    </Card>
  );
}

export default User;
