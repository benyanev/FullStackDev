import { useRef, useState } from 'react';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import LinearProgress from '@mui/material/LinearProgress';
import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { useAutoPlay } from '../../hooks/useAutoPlay';

const overlayButtonSx = {
  position: 'absolute',
  bgcolor: 'rgba(0,0,0,0.55)',
  color: 'white',
  '&:hover': { bgcolor: 'rgba(0,0,0,0.75)' },
};

/**
 * VideoPlayer — custom video interface for posts (no native browser controls).
 *
 * - Click anywhere on the video to play / pause; a big ▶ shows while paused.
 * - Mute / unmute button (starts muted, which browsers require for auto-play).
 * - Thin progress bar along the bottom.
 * - Auto-plays when scrolled into view and pauses when scrolled away (useAutoPlay).
 *
 * @param {Object} props
 * @param {string} props.src    - Full URL of the video file.
 * @param {number} [props.height=200] - Player height in px.
 */
function VideoPlayer({ src, height = 200 }) {
  const videoRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(true);
  const [progress, setProgress] = useState(0);

  useAutoPlay(videoRef);

  const togglePlay = () => {
    const video = videoRef.current;
    if (video.paused) {
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  };

  const toggleMute = (e) => {
    e.stopPropagation(); // don't also toggle play/pause
    videoRef.current.muted = !muted;
    setMuted(!muted);
  };

  const handleTimeUpdate = () => {
    const video = videoRef.current;
    if (video.duration) setProgress((video.currentTime / video.duration) * 100);
  };

  return (
    <Box
      onClick={togglePlay}
      sx={{ position: 'relative', bgcolor: 'black', cursor: 'pointer', height }}
      data-testid="video-player"
    >
      <video
        ref={videoRef}
        src={src}
        muted={muted}
        loop
        playsInline
        preload="metadata"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onTimeUpdate={handleTimeUpdate}
        style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
      />

      {/* Big play icon while paused */}
      {!playing && (
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
          }}
        >
          <PlayArrowRoundedIcon
            sx={{ fontSize: 64, color: 'white', bgcolor: 'rgba(0,0,0,0.45)', borderRadius: '50%' }}
          />
        </Box>
      )}

      {/* Mute / unmute */}
      <IconButton
        size="small"
        onClick={toggleMute}
        aria-label={muted ? 'Unmute' : 'Mute'}
        sx={{ ...overlayButtonSx, right: 8, bottom: 10 }}
      >
        {muted ? <VolumeOffIcon fontSize="small" /> : <VolumeUpIcon fontSize="small" />}
      </IconButton>

      {/* Progress bar */}
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 3 }}
      />
    </Box>
  );
}

export default VideoPlayer;
