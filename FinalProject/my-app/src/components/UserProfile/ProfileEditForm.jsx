import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';

/**
 * ProfileEditForm — name and bio editing fields with save/cancel buttons.
 *
 * @param {Object}   props
 * @param {string}   props.editName        - Current name field value.
 * @param {function} props.setEditName     - Name field setter.
 * @param {string}   props.editBio         - Current bio field value.
 * @param {function} props.setEditBio      - Bio field setter.
 * @param {string}   props.editError       - Error message to display.
 * @param {boolean}  props.saving          - Whether a save is in progress.
 * @param {function} props.onSave          - Save handler.
 * @param {function} props.onCancel        - Cancel handler.
 */
function ProfileEditForm({
  editName,
  setEditName,
  editBio,
  setEditBio,
  editError,
  saving,
  onSave,
  onCancel,
}) {
  return (
    <Box sx={{ mt: 2 }}>
      {editError && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
          {editError}
        </Alert>
      )}
      <TextField
        fullWidth
        label="Name"
        value={editName}
        onChange={(e) => setEditName(e.target.value)}
        sx={{ mb: 2 }}
        slotProps={{ inputLabel: { shrink: true } }}
      />
      <TextField
        fullWidth
        label="Bio"
        value={editBio}
        onChange={(e) => setEditBio(e.target.value)}
        multiline
        rows={3}
        sx={{ mb: 2 }}
        slotProps={{ inputLabel: { shrink: true } }}
      />
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          variant="contained"
          onClick={onSave}
          disabled={saving}
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #24476f 0%, #371f7d 100%)',
            },
          }}
        >
          {saving ? 'Saving...' : 'Save'}
        </Button>
        <Button
          variant="outlined"
          onClick={onCancel}
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            borderRadius: 2,
          }}
        >
          Cancel
        </Button>
      </Box>
    </Box>
  );
}

export default ProfileEditForm;
