import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useFollow } from '../../hooks/useFollow';
import { getAvatarColor } from '../../utils/avatarColor';
import FollowButton from './FollowButton';

/**
 * Displays a single user's information in a card with follow/unfollow capability.
 *
 * @param {Object} props
 * @param {number} props.id              - User ID (used for the "View Posts" link).
 * @param {string} props.name            - User's full name.
 * @param {string} props.email           - User's email address.
 * @param {number} props.followersCount  - Number of followers (optional).
 * @param {number} props.followingCount  - Number of users they follow (optional).
 */
function User({ id, name, email, followersCount = 0, followingCount = 0 }) {
  const { user } = useAuth();
  const {
    isFollowing,
    followLoading,
    localFollowersCount,
    handleToggleFollow,
    isOwnProfile,
  } = useFollow(id, followersCount);

  const avatarColor = getAvatarColor(name);

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
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography
              component={Link}
              to={`/profile/${id}`}
              variant="subtitle1"
              sx={{
                fontWeight: 700,
                lineHeight: 1.3,
                color: 'inherit',
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
              }}
            >
              {name}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {email}
            </Typography>
          </Box>
        </Box>

        {/* Followers / Following chips */}
        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
          <Chip
            label={`${localFollowersCount} followers`}
            size="small"
            variant="outlined"
            sx={{ fontWeight: 600, fontSize: '0.75rem' }}
          />
          <Chip
            label={`${followingCount} following`}
            size="small"
            variant="outlined"
            sx={{ fontWeight: 600, fontSize: '0.75rem' }}
          />
        </Box>
      </CardContent>

      {/* Action buttons */}
      <CardActions sx={{ px: 2.5, pb: 2, gap: 1 }}>
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

        {/* Follow/Unfollow — hidden for own card and when not logged in */}
        {user && !isOwnProfile && (
          <Box sx={{ ml: 'auto' }}>
            <FollowButton
              isFollowing={isFollowing}
              loading={followLoading}
              onClick={handleToggleFollow}
            />
          </Box>
        )}
      </CardActions>
    </Card>
  );
}

export default User;
