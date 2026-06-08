import { useState, useEffect } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import PersonRemoveIcon from '@mui/icons-material/PersonRemove';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { followUser, unfollowUser, checkIsFollowing } from '../services/api';

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
  const [isFollowing, setIsFollowing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [localFollowersCount, setLocalFollowersCount] = useState(followersCount);

  // Determine if this card is the logged-in user's own card
  const isOwnCard = user && user.id === id;

  // Check follow status on mount (only if logged in and not own card)
  useEffect(() => {
    if (user && !isOwnCard) {
      checkIsFollowing(id).then(setIsFollowing);
    }
  }, [user, id, isOwnCard]);

  // Sync followersCount prop when it changes
  useEffect(() => {
    setLocalFollowersCount(followersCount);
  }, [followersCount]);

  const handleToggleFollow = async () => {
    if (loading) return;
    setLoading(true);
    try {
      if (isFollowing) {
        await unfollowUser(id);
        setIsFollowing(false);
        setLocalFollowersCount((prev) => Math.max(0, prev - 1));
      } else {
        await followUser(id);
        setIsFollowing(true);
        setLocalFollowersCount((prev) => prev + 1);
      }
    } catch (err) {
      console.error('Follow/unfollow error:', err);
    } finally {
      setLoading(false);
    }
  };

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
        {user && !isOwnCard && (
          <Button
            size="small"
            variant={isFollowing ? 'outlined' : 'contained'}
            disabled={loading}
            onClick={handleToggleFollow}
            startIcon={isFollowing ? <PersonRemoveIcon /> : <PersonAddIcon />}
            sx={{
              textTransform: 'none',
              fontWeight: 600,
              borderRadius: 2,
              ml: 'auto',
              ...(isFollowing
                ? {
                    borderColor: 'rgba(211, 47, 47, 0.5)',
                    color: '#d32f2f',
                    '&:hover': {
                      borderColor: '#d32f2f',
                      background: 'rgba(211, 47, 47, 0.04)',
                    },
                  }
                : {
                    background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #24476f 0%, #371f7d 100%)',
                    },
                  }),
            }}
          >
            {loading ? '...' : isFollowing ? 'Unfollow' : 'Follow'}
          </Button>
        )}
      </CardActions>
    </Card>
  );
}

export default User;
