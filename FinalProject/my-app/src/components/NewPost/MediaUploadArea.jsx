import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const ACCEPTED_TYPES = 'image/png,image/jpeg,image/gif,image/webp,video/mp4,video/webm';

/**
 * MediaUploadArea — dropzone for attaching ONE image or video to a post,
 * with a preview and a remove button.
 *
 * @param {Object}          props
 * @param {string}          props.mediaPreview - Object URL of the selected file ('' if none).
 * @param {'image'|'video'|''} props.mediaType - Type of the selected file.
 * @param {function}        props.onSelect     - Handler for the file input change event.
 * @param {function}        props.onRemove     - Handler to remove the selected file.
 * @param {React.RefObject} props.fileInputRef - Ref to the hidden file input element.
 */
function MediaUploadArea({ mediaPreview, mediaType, onSelect, onRemove, fileInputRef }) {
  const previewSx = { width: '100%', maxHeight: 300, objectFit: 'cover', display: 'block' };

  return (
    <>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mb: 1, fontWeight: 500 }}
      >
        Attach Image or Video (optional)
      </Typography>
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_TYPES}
        onChange={onSelect}
        style={{ display: 'none' }}
        id="post-media-upload"
      />

      {!mediaPreview ? (
        <Box
          role="button"
          tabIndex={0}
          aria-label="Attach an image or video"
          onClick={() => fileInputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
          sx={{
            border: '2px dashed',
            borderColor: 'divider',
            borderRadius: 3,
            p: 3,
            mb: 3,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'rgba(30, 58, 95, 0.04)',
            },
          }}
        >
          <CloudUploadIcon
            sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }}
          />
          <Typography variant="body2" color="text.secondary">
            Click to upload an image (PNG, JPG, GIF, WebP — max 5 MB)
            <br />
            or a video (MP4, WebM — max 50 MB)
          </Typography>
        </Box>
      ) : (
        <Box
          sx={{
            position: 'relative',
            mb: 3,
            borderRadius: 3,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          {mediaType === 'video' ? (
            <Box component="video" src={mediaPreview} controls muted sx={previewSx} />
          ) : (
            <Box component="img" src={mediaPreview} alt="Preview" sx={previewSx} />
          )}
          <IconButton
            onClick={onRemove}
            aria-label="Remove attachment"
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              bgcolor: 'rgba(0,0,0,0.6)',
              color: 'white',
              '&:hover': { bgcolor: 'rgba(0,0,0,0.8)' },
            }}
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      )}
    </>
  );
}

export default MediaUploadArea;
