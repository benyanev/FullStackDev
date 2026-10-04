import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import WarningAmberRoundedIcon from '@mui/icons-material/WarningAmberRounded';

/**
 * ModerationDialog — shown when the backend blocks a post or comment as
 * toxic/hateful (HTTP 422). Nothing was published; the user keeps their
 * text and can edit it.
 *
 * @param {Object}   props
 * @param {string}   props.message - The backend's explanation ('' = closed).
 * @param {Function} props.onClose - Handler to close the dialog.
 */
function ModerationDialog({ message, onClose }) {
  return (
    <Dialog open={Boolean(message)} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 700 }}>
        <WarningAmberRoundedIcon color="warning" />
        Not published
      </DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained" sx={{ textTransform: 'none', fontWeight: 600 }}>
          Edit my text
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ModerationDialog;
