import { useEffect, useRef } from 'react';

/**
 * Shared hook that sets up an IntersectionObserver on a sentinel element
 * to trigger infinite-scroll loading.
 *
 * @param {() => void} loadMore - Callback to load the next page.
 * @param {boolean}    hasMore  - Whether more items are available.
 * @returns {React.RefObject} Ref to attach to the sentinel DOM element.
 */
export function useInfiniteScroll(loadMore, hasMore) {
  const sentinelRef = useRef(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { rootMargin: '200px' },
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loadMore]);

  return sentinelRef;
}
