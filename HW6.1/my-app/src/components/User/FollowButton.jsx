import Button from '@mui/material/Button';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import PersonRemoveIcon from '@mui/icons-material/PersonRemove';

/**
 * FollowButton — reusable follow/unfollow button with gradient/red styling.
 * Used by both the User card and the UserProfile page.
 *
 * @param {Object}   props
 * @param {boolean}  props.isFollowing - Whether the current user is following the target.
 * @param {boolean}  props.loading     - Whether a follow/unfollow request is in progress.
 * @param {function} props.onClick     - Handler for the toggle action.
 * @param {string}   [props.size]      - MUI Button size ('small' | 'medium' | 'large').
 */
function FollowButton({ isFollowing, loading, onClick, size = 'small' }) {
  return (
    <Button
      size={size}
      variant={isFollowing ? 'outlined' : 'contained'}
      disabled={loading}
      onClick={onClick}
      startIcon={isFollowing ? <PersonRemoveIcon /> : <PersonAddIcon />}
      sx={{
        textTransform: 'none',
        fontWeight: 600,
        borderRadius: 2,
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
  );
}

export default FollowButton;
