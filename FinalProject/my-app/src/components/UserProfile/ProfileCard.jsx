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
import AgentBadge from '../AgentBadge';

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
  pictureError,
  // Follower chips
  handleOpenFollowers,
  handleOpenFollowing,
}) {
  const avatarColor = getAvatarColor(profile.name);
  // Relative path (/static/uploads/...) — served through the Vite proxy / nginx
  const profilePicUrl = profile.profile_picture || null;

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
          height: { xs: 100, sm: 140 },
          background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
          borderRadius: '16px 16px 0 0',
        }}
      />

      <CardContent sx={{ px: { xs: 2.5, sm: 4 }, pb: { xs: 3, sm: 4 }, position: 'relative' }}>
        {/* Avatar — overlapping the banner */}
        <Box sx={{ position: 'relative', display: 'inline-block', mt: -8 }}>
          <Avatar
            src={profilePicUrl}
            sx={{
              width: { xs: 88, sm: 110 },
              height: { xs: 88, sm: 110 },
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
              aria-label="Change profile picture"
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

        {pictureError && (
          <Typography variant="caption" color="error" component="div" sx={{ mt: 1 }}>
            {pictureError}
          </Typography>
        )}

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
              right: { xs: 16, sm: 24 },
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
          <Box sx={{ position: 'absolute', top: 16, right: { xs: 16, sm: 24 } }}>
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
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                {profile.name}
              </Typography>
              {Boolean(profile.is_agent) && <AgentBadge />}
            </Box>
            {/* Emails are private: you only see your own */}
            {isOwnProfile && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1, overflowWrap: 'anywhere' }}>
                {currentUser.email}
              </Typography>
            )}
            {/* Agents show the personality that drives their posts & comments */}
            {Boolean(profile.is_agent) && profile.personality && (
              <Typography
                variant="body2"
                sx={{ mt: 1, p: 1.5, borderRadius: 2, bgcolor: 'action.hover', fontStyle: 'italic' }}
              >
                🤖 Personality — {profile.personality}
              </Typography>
            )}
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
