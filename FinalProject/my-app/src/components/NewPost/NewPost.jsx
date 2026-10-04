import { Navigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import { EditorContent } from '@tiptap/react';
import { useNewPost } from './useNewPost';
import MenuBar from './MenuBar';
import MediaUploadArea from './MediaUploadArea';
import ModerationDialog from '../ModerationDialog';
import AiAssistBar from './AiAssistBar';

/**
 * NewPost page — form for creating a new post with a title, rich text body (Tiptap),
 * an optional image or video attachment, and AI writing help (AiAssistBar).
 *
 * Auth guard: redirects unauthenticated users to /login.
 * Waits for the session check to complete before deciding.
 */
function NewPost() {
  const {
    title,
    setTitle,
    error,
    loading,
    uploading,
    mediaPreview,
    mediaType,
    fileInputRef,
    editor,
    user,
    authLoading,
    handleMediaSelect,
    removeMedia,
    handleSubmit,
    moderationMessage,
    closeModerationDialog,
  } = useNewPost();

  // Wait for session check to complete before redirecting
  if (authLoading) return null;

  // If not logged in, redirect to the login page
  if (!user) return <Navigate to="/login" replace />;

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', px: { xs: 2, sm: 3 }, py: { xs: 3, sm: 6 } }}>
      <Card
        sx={{
          width: '100%',
          maxWidth: 700,
          borderRadius: 3,
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.1)',
        }}
      >
        <CardContent sx={{ p: { xs: 2.5, sm: 4 } }}>
          <Typography
            variant="h5"
            sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}
          >
            Create New Post
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <AiAssistBar editor={editor} title={title} setTitle={setTitle} />

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              sx={{ mb: 2.5 }}
              slotProps={{
                inputLabel: { shrink: true },
                htmlInput: { 'data-testid': 'post-input' },
              }}
            />

            {/* Tiptap Rich Text Editor */}
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 0.5, fontWeight: 500 }}
            >
              Content
            </Typography>
            <Box
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 3,
                mb: 2.5,
                overflow: 'hidden',
                transition: 'border-color 0.2s',
                '&:focus-within': {
                  borderColor: 'primary.main',
                  boxShadow: '0 0 0 2px rgba(30, 58, 95, 0.15)',
                },
                '& .tiptap-editor': {
                  minHeight: 180,
                  maxHeight: 400,
                  overflowY: 'auto',
                  p: 2,
                  outline: 'none',
                  fontSize: '0.95rem',
                  lineHeight: 1.7,
                  '& p': { m: 0, mb: 0.5 },
                  '& ul, & ol': { pl: 3 },
                  '& blockquote': {
                    borderLeft: '3px solid',
                    borderColor: 'divider',
                    pl: 2,
                    ml: 0,
                    fontStyle: 'italic',
                    color: 'text.secondary',
                  },
                  '& code': {
                    bgcolor: 'action.hover',
                    borderRadius: 1,
                    px: 0.5,
                    fontFamily: 'monospace',
                    fontSize: '0.85em',
                  },
                  '& pre': {
                    bgcolor: 'grey.900',
                    color: 'grey.100',
                    borderRadius: 2,
                    p: 2,
                    fontFamily: 'monospace',
                    fontSize: '0.85em',
                    overflowX: 'auto',
                  },
                },
              }}
            >
              <MenuBar editor={editor} />
              <EditorContent editor={editor} data-testid="post-body" />
            </Box>

            <MediaUploadArea
              mediaPreview={mediaPreview}
              mediaType={mediaType}
              onSelect={handleMediaSelect}
              onRemove={removeMedia}
              fileInputRef={fileInputRef}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              data-testid="post-submit"
              sx={{
                borderRadius: 3,
                py: 1.3,
                textTransform: 'none',
                fontWeight: 600,
                fontSize: '1rem',
                background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
                '&:hover': {
                  background:
                    'linear-gradient(135deg, #24476f 0%, #371f7d 100%)',
                },
              }}
            >
              {uploading
                ? `Uploading ${mediaType}...`
                : loading
                  ? 'Publishing...'
                  : 'Publish Post'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      <ModerationDialog message={moderationMessage} onClose={closeModerationDialog} />
    </Box>
  );
}

export default NewPost;
