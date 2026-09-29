import { useEffect } from 'react';

/**
 * Auto-play on scroll: plays the video while at least `threshold` of it is
 * visible on screen, and pauses it when it scrolls out of view.
 *
 * Uses IntersectionObserver (the same browser API as useInfiniteScroll), so
 * nothing runs on every scroll event.
 *
 * @param {React.RefObject<HTMLVideoElement>} videoRef - Ref to the <video>.
 * @param {number} [threshold=0.6] - Visible fraction (0–1) that counts as "in view".
 */
export function useAutoPlay(videoRef, threshold = 0.6) {
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return undefined;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          // Browsers only allow auto-play for muted videos; if it is still
          // blocked, the user can press play themselves.
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      },
      { threshold },
    );

    observer.observe(video);
    return () => observer.disconnect();
  }, [videoRef, threshold]);
}
