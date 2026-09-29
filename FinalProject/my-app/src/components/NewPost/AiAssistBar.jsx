import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import CircularProgress from '@mui/material/CircularProgress';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SpellcheckIcon from '@mui/icons-material/Spellcheck';
import { autocorrectText, suggestPost } from '../../services/ai.service';

const MAX_TOPIC_LENGTH = 200;

const buttonSx = { textTransform: 'none', fontWeight: 600, borderRadius: 2 };

/**
 * AiAssistBar — AI writing help for the NewPost form.
 * - "Fix grammar": corrects the title and the editor content in place.
 * - "Write it for me": asks for a topic and fills in a suggested title + body.
 *
 * @param {Object}   props
 * @param {Object}   props.editor   - The Tiptap editor instance.
 * @param {string}   props.title    - Current post title.
 * @param {Function} props.setTitle - Setter for the post title.
 */
function AiAssistBar({ editor, title, setTitle }) {
  const [busy, setBusy] = useState('');          // '' | 'fix' | 'suggest'
  const [error, setError] = useState('');
  const [topicOpen, setTopicOpen] = useState(false);
  const [topic, setTopic] = useState('');

  const handleFix = async () => {
    setError('');
    const bodyHtml = editor.getText().trim() ? editor.getHTML() : '';
    if (!title.trim() && !bodyHtml) {
      setError('Write something first, then I can fix it.');
      return;
    }

    setBusy('fix');
    try {
      const [fixedTitle, fixedBody] = await Promise.all([
        title.trim() ? autocorrectText(title) : null,
        bodyHtml ? autocorrectText(bodyHtml) : null,
      ]);
      if (fixedTitle) setTitle(fixedTitle.text);
      if (fixedBody) editor.commands.setContent(fixedBody.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  };

  const handleSuggest = async () => {
    setError('');
    setTopicOpen(false);
    setBusy('suggest');
    try {
      const post = await suggestPost(topic.trim());
      setTitle(post.title);
      editor.commands.setContent(post.body);
      setTopic('');
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  };

  return (
    <Box sx={{ mb: 2.5 }}>
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button
          variant="outlined"
          size="small"
          sx={buttonSx}
          startIcon={busy === 'suggest' ? <CircularProgress size={16} /> : <AutoAwesomeIcon />}
          disabled={Boolean(busy)}
          onClick={() => setTopicOpen(true)}
        >
          Write it for me
        </Button>
        <Button
          variant="outlined"
          size="small"
          sx={buttonSx}
          startIcon={busy === 'fix' ? <CircularProgress size={16} /> : <SpellcheckIcon />}
          disabled={Boolean(busy)}
          onClick={handleFix}
        >
          Fix grammar
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mt: 1.5, borderRadius: 2 }}>{error}</Alert>}

      {/* Topic prompt for "Write it for me" */}
      <Dialog open={topicOpen} onClose={() => setTopicOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>✨ What should the post be about?</DialogTitle>
        <DialogContent>
          <TextField
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. my first time hiking in the Galilee"
            fullWidth
            autoFocus
            slotProps={{ htmlInput: { maxLength: MAX_TOPIC_LENGTH } }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && topic.trim()) handleSuggest();
            }}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTopicOpen(false)} sx={{ textTransform: 'none' }}>
            Cancel
          </Button>
          <Button onClick={handleSuggest} variant="contained" disabled={!topic.trim()} sx={buttonSx}>
            Write post
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AiAssistBar;
