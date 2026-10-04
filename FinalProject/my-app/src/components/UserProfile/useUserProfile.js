import { useState, useRef, useCallback, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchUser } from '../../services/users.service';
import { fetchUserPosts } from '../../services/posts.service';
import { fetchFollowers, fetchFollowing } from '../../services/follows.service';
import { updateProfile, uploadProfilePicture } from '../../services/profile.service';
import { useAuth } from '../../context/AuthContext';

const POSTS_LIMIT = 10;

/**
 * Custom hook for the UserProfile page.
 * Manages profile data, editing, picture upload, posts pagination,
 * and followers/following dialog data.
 *
 * @returns {Object} All state and handlers needed by the UserProfile component tree.
 */
export function useUserProfile() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();

  // Profile data
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Posts
  const [posts, setPosts] = useState([]);
  const [postsLoading, setPostsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const startRef = useRef(0);
  const postsLoadingRef = useRef(false);
  const requestIdRef = useRef(0); // ignore answers to outdated loads (see useFeed)
  const [pictureError, setPictureError] = useState('');

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

  const loadPosts = useCallback(async (reset = false) => {
    // "Load more" waits for the current request; a reset always starts fresh
    if (postsLoadingRef.current && !reset) return;
    const requestId = ++requestIdRef.current;
    postsLoadingRef.current = true;
    setPostsLoading(true);
    try {
      const start = reset ? 0 : startRef.current;
      const newPosts = await fetchUserPosts(userId, start, POSTS_LIMIT);
      if (requestId !== requestIdRef.current) return; // e.g. moved to another profile

      if (reset) {
        setPosts(newPosts);
        startRef.current = POSTS_LIMIT;
      } else {
        // skip posts already shown (new posts shift the pages)
        setPosts((prev) => {
          const shown = new Set(prev.map((p) => p.id));
          return [...prev, ...newPosts.filter((p) => !shown.has(p.id))];
        });
        startRef.current += POSTS_LIMIT;
      }
      setHasMore(newPosts.length === POSTS_LIMIT);
    } catch (err) {
      console.error('Error loading posts:', err);
      if (requestId === requestIdRef.current) setHasMore(false);
    } finally {
      if (requestId === requestIdRef.current) {
        setPostsLoading(false);
        postsLoadingRef.current = false;
      }
    }
  }, [userId]);

  // Fetch profile data
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setProfile(null);
    setPosts([]);
    startRef.current = 0;
    setEditing(false);

    fetchUser(userId)
      .then((data) => {
        setProfile(data);
        setEditName(data.name || '');
        setEditBio(data.bio || '');
      })
      .catch(console.error)
      .finally(() => setLoading(false));

    // Load initial posts
    loadPosts(true);
  }, [userId, loadPosts]);

  // loadMore wrapper for infinite scroll (never resets)
  const loadMorePosts = useCallback(() => {
    loadPosts(false);
  }, [loadPosts]);

  // Profile picture upload
  const handlePictureUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setPictureError('');
    try {
      const { url } = await uploadProfilePicture(file);
      await updateProfile(Number(userId), { profile_picture: url });
      setProfile((prev) => ({ ...prev, profile_picture: url }));
    } catch (err) {
      setPictureError(err.message); // e.g. wrong file type or too large
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

  // Cancel editing
  const handleCancelEdit = () => {
    setEditing(false);
    setEditName(profile.name);
    setEditBio(profile.bio || '');
    setEditError('');
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

  // Allow the follow hook in UserProfile to update the profile's followers_count
  const updateFollowersCount = (delta) => {
    setProfile((prev) => ({
      ...prev,
      followers_count: Math.max(0, (prev.followers_count || 0) + delta),
    }));
  };

  return {
    userId,
    currentUser,
    profile,
    loading,
    isOwnProfile,

    // Posts
    posts,
    postsLoading,
    hasMore,
    loadMorePosts,

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

    // Dialogs
    followersDialog,
    setFollowersDialog,
    followingDialog,
    setFollowingDialog,
    followersList,
    followingList,
    handleOpenFollowers,
    handleOpenFollowing,

    updateFollowersCount,
  };
}
