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
  // Every load gets a number; answers to older loads are ignored (e.g. the
  // user switched tab while a page was still loading)
  const requestIdRef = useRef(0);

  const loadPosts = useCallback(async (reset = false, tab = activeTabRef.current) => {
    // "Load more" waits for the current request; a reset always starts fresh
    if (loadingRef.current && !reset) return;
    const requestId = ++requestIdRef.current;
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

      if (requestId !== requestIdRef.current) return; // outdated answer

      if (reset) {
        setPosts(newPosts);
        startRef.current = LIMIT;
      } else {
        // New posts shift the pages while scrolling (bots post every minute),
        // so skip posts that are already on screen instead of showing them twice
        setPosts((prev) => {
          const shown = new Set(prev.map((p) => p.id));
          return [...prev, ...newPosts.filter((p) => !shown.has(p.id))];
        });
        startRef.current += LIMIT;
      }

      setHasMore(newPosts.length === LIMIT);
    } catch (error) {
      console.error('Error fetching posts:', error);
      if (requestId === requestIdRef.current) setHasMore(false); // stop retrying forever
    } finally {
      if (requestId === requestIdRef.current) {
        setLoading(false);
        loadingRef.current = false;
      }
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
        fetchUser(userId)
          .then((u) => setUserName(u.name))
          .catch(() => setUserName('Unknown user'));
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
    : activeTab === 1 && user
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
