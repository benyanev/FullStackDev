import { useState } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import { reportPost } from '../../services/reports.service';

const MAX_REASON_LENGTH = 500;

/**
 * ReportDialog — asks for a reason and reports a post to the moderators.
 *
 * @param {Object}   props
 * @param {number}   props.postId  - The post being reported.
 * @param {boolean}  props.open    - Whether the dialog is open.
 * @param {Function} props.onClose - Handler to close the dialog.
 */
function ReportDialog({ postId, open, onClose }) {
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleClose = () => {
    setReason('');
    setError('');
    setMessage('');
    onClose();
  };

  const handleSubmit = async () => {
    setError('');
    setSubmitting(true);
    try {
      const data = await reportPost(postId, reason.trim());
      setMessage(data.message);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>Report post</DialogTitle>
      <DialogContent>
        {message ? (
          <Alert severity="success">{message}</Alert>
        ) : (
          <>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <TextField
              id={`report-reason-${postId}`}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Why should a moderator review this post?"
              fullWidth
              multiline
              minRows={3}
              autoFocus
              slotProps={{ htmlInput: { maxLength: MAX_REASON_LENGTH } }}
              helperText={`${reason.length}/${MAX_REASON_LENGTH}`}
              sx={{ mt: 1 }}
            />
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} sx={{ textTransform: 'none' }}>
          {message ? 'Close' : 'Cancel'}
        </Button>
        {!message && (
          <Button
            onClick={handleSubmit}
            variant="contained"
            color="error"
            disabled={!reason.trim() || submitting}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            {submitting ? 'Sending…' : 'Report'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default ReportDialog;
