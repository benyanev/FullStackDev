import { useState, useEffect } from 'react';
import { followUser, unfollowUser, checkIsFollowing } from '../services/follows.service';
import { useAuth } from '../context/AuthContext';

/**
 * Shared hook for follow/unfollow logic.
 * Used by both the User card and the UserProfile page.
 *
 * @param {number} targetUserId - ID of the user to follow/unfollow.
 * @param {number} initialFollowersCount - Starting followers count.
 * @returns {{
 *   isFollowing: boolean,
 *   followLoading: boolean,
 *   localFollowersCount: number,
 *   handleToggleFollow: () => Promise<void>,
 *   isOwnProfile: boolean,
 * }}
 */
export function useFollow(targetUserId, initialFollowersCount = 0) {
  const { user } = useAuth();
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  
  // Track delta instead of copying props to state (avoids useEffect sync)
  const [followerDelta, setFollowerDelta] = useState(0);

  const isOwnProfile = user && user.id === Number(targetUserId);

  // Check follow status on mount
  useEffect(() => {
    if (user && !isOwnProfile) {
      checkIsFollowing(Number(targetUserId)).then(setIsFollowing);
    }
  }, [user, targetUserId, isOwnProfile]);

  const handleToggleFollow = async () => {
    if (followLoading) return;
    setFollowLoading(true);
    try {
      if (isFollowing) {
        await unfollowUser(Number(targetUserId));
        setIsFollowing(false);
        setFollowerDelta((prev) => prev - 1);
      } else {
        await followUser(Number(targetUserId));
        setIsFollowing(true);
        setFollowerDelta((prev) => prev + 1);
      }
    } catch (err) {
      console.error('Follow/unfollow error:', err);
    } finally {
      setFollowLoading(false);
    }
  };

  const localFollowersCount = Math.max(0, initialFollowersCount + followerDelta);

  return { isFollowing, followLoading, localFollowersCount, handleToggleFollow, isOwnProfile };
}
