import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Alert from '@mui/material/Alert';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import EditIcon from '@mui/icons-material/Edit';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import PersonRemoveIcon from '@mui/icons-material/PersonRemove';
import CloseIcon from '@mui/icons-material/Close';
import { useAuth } from '../context/AuthContext';
import {
  fetchUser,
  fetchUserPosts,
  fetchFollowers,
  fetchFollowing,
  followUser,
  unfollowUser,
  checkIsFollowing,
  updateProfile,
  uploadProfilePicture,
} from '../services/api';
import SinglePost from './SinglePost';

const POSTS_LIMIT = 10;
const BACKEND_URL = 'http://localhost:5000';

/**
 * UserProfile — dedicated profile page showing user info, bio,
 * profile picture, follower/following counts with dialogs,
 * follow/unfollow button, edit profile, and the user's posts.
 */
function UserProfile() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();

  // Profile data
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Follow state
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);

  // Posts
  const [posts, setPosts] = useState([]);
  const [postsLoading, setPostsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const startRef = useRef(0);
  const postsLoadingRef = useRef(false);
  const postsSentinelRef = useRef(null);

  // Edit mode
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editBio, setEditBio] = useState('');
  const [editError, setEditError] = useState('');
  const [saving, setSaving] = useState(false);

  // Followers/Following dialogs
  const [followersDialog, setFollowersDialog] = useState(false);
  const [followingDialog, setFollowingDialog] = useState(false);
  const [followersList, setFollowersList] = useState([]);
  const [followingList, setFollowingList] = useState([]);

  const isOwnProfile = currentUser && currentUser.id === Number(userId);

  // Fetch profile data
  useEffect(() => {
    setLoading(true);
    setProfile(null);
    setPosts([]);
    startRef.current = 0;
    hasMoreRef.current = true;

    fetchUser(userId)
      .then((data) => {
        setProfile(data);
        setEditName(data.name || '');
        setEditBio(data.bio || '');
      })
      .catch(console.error)
      .finally(() => setLoading(false));

    // Check follow status
    if (currentUser && !isOwnProfile) {
      checkIsFollowing(Number(userId)).then(setIsFollowing);
    }

    // Load initial posts
    loadPosts(true);
  }, [userId, currentUser]);

  const loadPosts = useCallback(async (reset = false) => {
    if (postsLoadingRef.current) return;
    postsLoadingRef.current = true;
    setPostsLoading(true);
    try {
      const start = reset ? 0 : startRef.current;
      const newPosts = await fetchUserPosts(userId, start, POSTS_LIMIT);
      if (reset) {
        setPosts(newPosts);
        startRef.current = POSTS_LIMIT;
      } else {
        setPosts((prev) => [...prev, ...newPosts]);
        startRef.current += POSTS_LIMIT;
      }
      setHasMore(newPosts.length === POSTS_LIMIT);
    } catch (err) {
      console.error('Error loading posts:', err);
    } finally {
      setPostsLoading(false);
      postsLoadingRef.current = false;
    }
  }, [userId]);

  // IntersectionObserver for infinite scroll on user posts
  useEffect(() => {
    const sentinel = postsSentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !postsLoadingRef.current && hasMore) {
          loadPosts(false);
        }
      },
      { rootMargin: '200px' }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loadPosts]);

  // Follow/Unfollow
  const handleToggleFollow = async () => {
    if (followLoading) return;
    setFollowLoading(true);
    try {
      if (isFollowing) {
        await unfollowUser(Number(userId));
        setIsFollowing(false);
        setProfile((prev) => ({
          ...prev,
          followers_count: Math.max(0, (prev.followers_count || 0) - 1),
        }));
      } else {
        await followUser(Number(userId));
        setIsFollowing(true);
        setProfile((prev) => ({
          ...prev,
          followers_count: (prev.followers_count || 0) + 1,
        }));
      }
    } catch (err) {
      console.error('Follow error:', err);
    } finally {
      setFollowLoading(false);
    }
  };

  // Profile picture upload
  const handlePictureUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const { url } = await uploadProfilePicture(file);
      await updateProfile(Number(userId), { profile_picture: url });
      setProfile((prev) => ({ ...prev, profile_picture: url }));
    } catch (err) {
      console.error('Upload error:', err);
    }
  };

  // Save profile edits
  const handleSaveProfile = async () => {
    setEditError('');
    if (!editName.trim()) {
      setEditError('Name cannot be empty.');
      return;
    }
    setSaving(true);
    try {
      const { user: updated } = await updateProfile(Number(userId), {
        name: editName.trim(),
        bio: editBio,
      });
      setProfile((prev) => ({ ...prev, ...updated }));
      setEditing(false);
    } catch (err) {
      setEditError(err.message);
    } finally {
      setSaving(false);
    }
  };

  // Open followers/following dialogs
  const handleOpenFollowers = async () => {
    try {
      const data = await fetchFollowers(Number(userId));
      setFollowersList(data.users);
      setFollowersDialog(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpenFollowing = async () => {
    try {
      const data = await fetchFollowing(Number(userId));
      setFollowingList(data.users);
      setFollowingDialog(true);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', px: 3, py: 6 }}>
        <Alert severity="error">User not found.</Alert>
      </Box>
    );
  }

  const avatarColor = `hsl(${[...profile.name].reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360}, 55%, 50%)`;
  const profilePicUrl = profile.profile_picture
    ? `${BACKEND_URL}${profile.profile_picture}`
    : null;

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', px: 3, py: 4 }}>
      {/* Profile Card */}
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
            <Button
              variant={isFollowing ? 'outlined' : 'contained'}
              disabled={followLoading}
              onClick={handleToggleFollow}
              startIcon={isFollowing ? <PersonRemoveIcon /> : <PersonAddIcon />}
              sx={{
                position: 'absolute',
                top: 16,
                right: 24,
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
              {followLoading ? '...' : isFollowing ? 'Unfollow' : 'Follow'}
            </Button>
          )}

          {/* Name & Bio */}
          {editing ? (
            <Box sx={{ mt: 2 }}>
              {editError && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                  {editError}
                </Alert>
              )}
              <TextField
                fullWidth
                label="Name"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                sx={{ mb: 2 }}
                slotProps={{ inputLabel: { shrink: true } }}
              />
              <TextField
                fullWidth
                label="Bio"
                value={editBio}
                onChange={(e) => setEditBio(e.target.value)}
                multiline
                rows={3}
                sx={{ mb: 2 }}
                slotProps={{ inputLabel: { shrink: true } }}
              />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleSaveProfile}
                  disabled={saving}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #24476f 0%, #371f7d 100%)',
                    },
                  }}
                >
                  {saving ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setEditing(false);
                    setEditName(profile.name);
                    setEditBio(profile.bio || '');
                    setEditError('');
                  }}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: 2,
                  }}
                >
                  Cancel
                </Button>
              </Box>
            </Box>
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

      {/* User's Posts */}
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
        Posts
      </Typography>

      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid key={post.id} size={{ xs: 12, sm: 6, md: 4 }}>
            <SinglePost
              title={post.title}
              email={post.email}
              body={post.body}
              authorId={post.userId}
              authorName={post.authorName}
              createdAt={post.created_at}
              imageUrl={post.image_url}
            />
          </Grid>
        ))}
      </Grid>

      {posts.length === 0 && !postsLoading && (
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ textAlign: 'center', mt: 2 }}
        >
          No posts yet.
        </Typography>
      )}

      {/* Load More */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, mb: 2 }}>
        {postsLoading && <CircularProgress size={36} thickness={4} />}
      </Box>

      {/* Sentinel element for infinite scroll */}
      {hasMore && <div ref={postsSentinelRef} style={{ height: 1 }} />}

      {/* End of posts message */}
      {!hasMore && posts.length > 0 && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ textAlign: 'center', mt: 2, mb: 2, fontStyle: 'italic' }}
        >
          You've reached the end
        </Typography>
      )}

      {/* Followers Dialog */}
      <Dialog
        open={followersDialog}
        onClose={() => setFollowersDialog(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', fontWeight: 700 }}>
          Followers
          <IconButton
            onClick={() => setFollowersDialog(false)}
            sx={{ ml: 'auto' }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {followersList.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
              No followers yet.
            </Typography>
          ) : (
            <List disablePadding>
              {followersList.map((u) => {
                const color = `hsl(${[...u.name].reduce((a, c) => a + c.charCodeAt(0), 0) % 360}, 55%, 50%)`;
                return (
                  <ListItem key={u.id}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: color, width: 36, height: 36, fontSize: 16 }}>
                        {u.name[0].toUpperCase()}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {u.name}
                        </Typography>
                      }
                      secondary={u.email}
                    />
                  </ListItem>
                );
              })}
            </List>
          )}
        </DialogContent>
      </Dialog>

      {/* Following Dialog */}
      <Dialog
        open={followingDialog}
        onClose={() => setFollowingDialog(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', fontWeight: 700 }}>
          Following
          <IconButton
            onClick={() => setFollowingDialog(false)}
            sx={{ ml: 'auto' }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {followingList.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
              Not following anyone yet.
            </Typography>
          ) : (
            <List disablePadding>
              {followingList.map((u) => {
                const color = `hsl(${[...u.name].reduce((a, c) => a + c.charCodeAt(0), 0) % 360}, 55%, 50%)`;
                return (
                  <ListItem key={u.id}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: color, width: 36, height: 36, fontSize: 16 }}>
                        {u.name[0].toUpperCase()}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {u.name}
                        </Typography>
                      }
                      secondary={u.email}
                    />
                  </ListItem>
                );
              })}
            </List>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}

export default UserProfile;
