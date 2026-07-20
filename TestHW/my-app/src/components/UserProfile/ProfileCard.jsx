import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import { getAvatarColor } from '../../utils/avatarColor';
import FollowButton from '../User/FollowButton';
import ProfileEditForm from './ProfileEditForm';

const BACKEND_URL = 'http://localhost:5000';

/**
 * ProfileCard — the top section of the user profile page.
 * Displays the banner, avatar (with camera overlay for own profile),
 * action button (Edit / Follow), name & bio (or edit form), and follower chips.
 *
 * @param {Object} props - All props are passed through from UserProfile.
 */
function ProfileCard({
  profile,
  isOwnProfile,
  currentUser,
  // Follow
  isFollowing,
  followLoading,
  handleToggleFollow,
  // Edit
  editing,
  setEditing,
  editName,
  setEditName,
  editBio,
  setEditBio,
  editError,
  saving,
  handleSaveProfile,
  handleCancelEdit,
  handlePictureUpload,
  // Follower chips
  handleOpenFollowers,
  handleOpenFollowing,
}) {
  const avatarColor = getAvatarColor(profile.name);
  const profilePicUrl = profile.profile_picture
    ? `${BACKEND_URL}${profile.profile_picture}`
    : null;

  return (
    <Card
      sx={{
        borderRadius: 4,
        overflow: 'visible',
        boxShadow: '0 8px 40px rgba(0, 0, 0, 0.1)',
        mb: 4,
      }}
    >
      {/* Banner gradient */}
      <Box
        sx={{
          height: 140,
          background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
          borderRadius: '16px 16px 0 0',
        }}
      />

      <CardContent sx={{ px: 4, pb: 4, position: 'relative' }}>
        {/* Avatar — overlapping the banner */}
        <Box sx={{ position: 'relative', display: 'inline-block', mt: -8 }}>
          <Avatar
            src={profilePicUrl}
            sx={{
              width: 110,
              height: 110,
              bgcolor: avatarColor,
              fontSize: 42,
              fontWeight: 700,
              border: '4px solid white',
              boxShadow: '0 4px 14px rgba(0, 0, 0, 0.15)',
            }}
          >
            {profile.name[0].toUpperCase()}
          </Avatar>
          {/* Camera icon to change picture (own profile only) */}
          {isOwnProfile && (
            <IconButton
              component="label"
              size="small"
              sx={{
                position: 'absolute',
                bottom: 2,
                right: 2,
                bgcolor: 'white',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                '&:hover': { bgcolor: '#f5f5f5' },
              }}
            >
              <CameraAltIcon fontSize="small" />
              <input
                type="file"
                hidden
                accept="image/png,image/jpeg,image/gif,image/webp"
                onChange={handlePictureUpload}
              />
            </IconButton>
          )}
        </Box>

        {/* Edit button (own profile) */}
        {isOwnProfile && !editing && (
          <Button
            startIcon={<EditIcon />}
            size="small"
            variant="outlined"
            onClick={() => setEditing(true)}
            sx={{
              position: 'absolute',
              top: 16,
              right: 24,
              textTransform: 'none',
              fontWeight: 600,
              borderRadius: 2,
            }}
          >
            Edit Profile
          </Button>
        )}

        {/* Follow/Unfollow button (other users) */}
        {currentUser && !isOwnProfile && (
          <Box sx={{ position: 'absolute', top: 16, right: 24 }}>
            <FollowButton
              isFollowing={isFollowing}
              loading={followLoading}
              onClick={handleToggleFollow}
            />
          </Box>
        )}

        {/* Name & Bio — edit form or display */}
        {editing ? (
          <ProfileEditForm
            editName={editName}
            setEditName={setEditName}
            editBio={editBio}
            setEditBio={setEditBio}
            editError={editError}
            saving={saving}
            onSave={handleSaveProfile}
            onCancel={handleCancelEdit}
          />
        ) : (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              {profile.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {profile.email}
            </Typography>
            {profile.bio && (
              <Typography
                variant="body1"
                sx={{ mt: 1, color: 'text.secondary', lineHeight: 1.6 }}
              >
                {profile.bio}
              </Typography>
            )}
          </Box>
        )}

        <Divider sx={{ my: 2 }} />

        {/* Followers / Following counts — clickable */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip
            label={`${profile.followers_count || 0} followers`}
            onClick={handleOpenFollowers}
            variant="outlined"
            sx={{
              fontWeight: 600,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.04)' },
            }}
          />
          <Chip
            label={`${profile.following_count || 0} following`}
            onClick={handleOpenFollowing}
            variant="outlined"
            sx={{
              fontWeight: 600,
              cursor: 'pointer',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.04)' },
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
}

export default ProfileCard;
