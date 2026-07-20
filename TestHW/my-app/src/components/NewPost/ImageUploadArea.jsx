import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

/**
 * ImageUploadArea — dropzone for selecting a post image, with preview and remove button.
 *
 * @param {Object}         props
 * @param {string}         props.imagePreview  - Object URL of the selected image (empty if none).
 * @param {function}       props.onSelect      - Handler for the file input change event.
 * @param {function}       props.onRemove      - Handler to remove the selected image.
 * @param {React.RefObject} props.fileInputRef - Ref to the hidden file input element.
 */
function ImageUploadArea({ imagePreview, onSelect, onRemove, fileInputRef }) {
  return (
    <>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mb: 1, fontWeight: 500 }}
      >
        Attach Image (optional)
      </Typography>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/gif,image/webp"
        onChange={onSelect}
        style={{ display: 'none' }}
        id="post-image-upload"
      />

      {!imagePreview ? (
        <Box
          onClick={() => fileInputRef.current?.click()}
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
          <Box
            component="img"
            src={imagePreview}
            alt="Preview"
            sx={{
              width: '100%',
              maxHeight: 300,
              objectFit: 'cover',
              display: 'block',
            }}
          />
          <IconButton
            onClick={onRemove}
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

export default ImageUploadArea;
