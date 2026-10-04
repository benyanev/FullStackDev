import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import { useFollow } from '../../hooks/useFollow';
import { useInfiniteScroll } from '../../hooks/useInfiniteScroll';
import { useUserProfile } from './useUserProfile';
import ProfileCard from './ProfileCard';
import UserListDialog from './UserListDialog';
import SinglePost from '../SinglePost/SinglePost';

/**
 * UserProfile — dedicated profile page showing user info, bio,
 * profile picture, follower/following counts with dialogs,
 * follow/unfollow button, edit profile, and the user's posts.
 */
function UserProfile() {
  const {
    userId,
    currentUser,
    profile,
    loading,
    isOwnProfile,

    posts,
    postsLoading,
    hasMore,
    loadMorePosts,

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

    followersDialog,
    setFollowersDialog,
    followingDialog,
    setFollowingDialog,
    followersList,
    followingList,
    handleOpenFollowers,
    handleOpenFollowing,

    updateFollowersCount,
  } = useUserProfile();

  const {
    isFollowing,
    followLoading,
    handleToggleFollow: rawToggleFollow,
  } = useFollow(userId, profile?.followers_count || 0);

  // Wrap the toggle to also update the profile card's followers_count
  const handleToggleFollow = async () => {
    const wasfollowing = isFollowing;
    await rawToggleFollow();
    // After toggle, update the profile's count in the opposite direction
    updateFollowersCount(wasfollowing ? -1 : 1);
  };

  const sentinelRef = useInfiniteScroll(loadMorePosts, hasMore);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', px: { xs: 2, sm: 3 }, py: { xs: 3, sm: 6 } }}>
        <Alert severity="error">User not found.</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', px: { xs: 2, sm: 3 }, py: { xs: 2.5, sm: 4 } }}>
      <ProfileCard
        profile={profile}
        isOwnProfile={isOwnProfile}
        currentUser={currentUser}
        isFollowing={isFollowing}
        followLoading={followLoading}
        handleToggleFollow={handleToggleFollow}
        editing={editing}
        setEditing={setEditing}
        editName={editName}
        setEditName={setEditName}
        editBio={editBio}
        setEditBio={setEditBio}
        editError={editError}
        saving={saving}
        handleSaveProfile={handleSaveProfile}
        handleCancelEdit={handleCancelEdit}
        handlePictureUpload={handlePictureUpload}
        pictureError={pictureError}
        handleOpenFollowers={handleOpenFollowers}
        handleOpenFollowing={handleOpenFollowing}
      />

      {/* User's Posts */}
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
        Posts
      </Typography>

      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid key={post.id} size={{ xs: 12, sm: 6, md: 4 }}>
            <SinglePost
              postId={post.id}
              title={post.title}
              body={post.body}
              authorId={post.userId}
              authorName={post.authorName}
              authorIsAgent={Boolean(post.authorIsAgent)}
              createdAt={post.created_at}
              imageUrl={post.image_url}
              videoUrl={post.video_url}
              likeCount={post.like_count}
              commentCount={post.comment_count}
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
      {hasMore && <div ref={sentinelRef} style={{ height: 1 }} />}

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

      {/* Followers / Following Dialogs */}
      <UserListDialog
        open={followersDialog}
        onClose={() => setFollowersDialog(false)}
        title="Followers"
        users={followersList}
        emptyMessage="No followers yet."
      />
      <UserListDialog
        open={followingDialog}
        onClose={() => setFollowingDialog(false)}
        title="Following"
        users={followingList}
        emptyMessage="Not following anyone yet."
      />
    </Box>
  );
}

export default UserProfile;
