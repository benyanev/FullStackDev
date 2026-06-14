import { useState, useRef, useCallback, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPosts, fetchUserPosts, fetchFollowingPosts } from '../../services/posts.service';
import { fetchUser } from '../../services/users.service';
import { useAuth } from '../../context/AuthContext';

const LIMIT = 10;

/**
 * Custom hook for the Feed component.
 * Manages post fetching across three modes (global, following, user-specific),
 * tab switching, pagination state, and provides a loading-guarded loadMore
 * callback for the infinite scroll hook.
 *
 * @returns {{
 *   posts: Array,
 *   loading: boolean,
 *   hasMore: boolean,
 *   loadMore: () => void,
 *   userName: string,
 *   userId: string|undefined,
 *   activeTab: number,
 *   handleTabChange: (event: any, newValue: number) => void,
 *   user: Object|null,
 *   heading: string,
 * }}
 */
export function useFeed() {
  const { userId } = useParams();
  const { user } = useAuth();

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userName, setUserName] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const startRef = useRef(0);
  const hasFetched = useRef(false);
  const prevUserIdRef = useRef(userId);
  const loadingRef = useRef(false);
  const activeTabRef = useRef(activeTab);

  const loadPosts = useCallback(async (reset = false, tab = activeTabRef.current) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    try {
      const start = reset ? 0 : startRef.current;

      let newPosts;
      if (userId) {
        newPosts = await fetchUserPosts(userId, start, LIMIT);
      } else if (tab === 1 && user) {
        newPosts = await fetchFollowingPosts(start, LIMIT);
      } else {
        newPosts = await fetchPosts(start, LIMIT);
      }

      if (reset) {
        setPosts(newPosts);
        startRef.current = LIMIT;
      } else {
        setPosts((prev) => [...prev, ...newPosts]);
        startRef.current += LIMIT;
      }

      setHasMore(newPosts.length === LIMIT);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
      loadingRef.current = false;
    }
  }, [userId, user]);

  // loadMore wrapper for infinite scroll (never resets)
  const loadMore = useCallback(() => {
    loadPosts(false);
  }, [loadPosts]);

  // Fetch on mount and reset when userId changes
  useEffect(() => {
    if (prevUserIdRef.current !== userId) {
      prevUserIdRef.current = userId;
      hasFetched.current = false;
      startRef.current = 0;
      setHasMore(true);
    }

    if (!hasFetched.current) {
      hasFetched.current = true;

      if (userId) {
        fetchUser(userId).then((u) => setUserName(u.name));
      } else {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setUserName('');
      }

      loadPosts(true);
    }
  }, [userId, loadPosts]);

  // Handle tab change
  const handleTabChange = (_event, newValue) => {
    setActiveTab(newValue);
    activeTabRef.current = newValue;
    startRef.current = 0;
    setPosts([]);
    setHasMore(true);
    loadPosts(true, newValue);
  };

  // Heading text
  const heading = userId
    ? `Posts by ${userName || '...'}`
    : activeTab === 1
      ? 'Following Feed'
      : 'Latest Posts';

  return {
    posts,
    loading,
    hasMore,
    loadMore,
    userName,
    userId,
    activeTab,
    handleTabChange,
    user,
    heading,
  };
}
