import { useState, useRef, useCallback } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Divider from '@mui/material/Divider';
import FormatBoldIcon from '@mui/icons-material/FormatBold';
import FormatItalicIcon from '@mui/icons-material/FormatItalic';
import StrikethroughSIcon from '@mui/icons-material/StrikethroughS';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import CodeIcon from '@mui/icons-material/Code';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';
import ImageIcon from '@mui/icons-material/Image';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { useAuth } from '../context/AuthContext';
import { createPost, uploadPostImage } from '../services/api';

/**
 * MenuBar — toolbar for the Tiptap rich text editor.
 * Provides formatting buttons for bold, italic, lists, code, blockquote, etc.
 */
function MenuBar({ editor }) {
  if (!editor) return null;

  const buttons = [
    {
      icon: <FormatBoldIcon fontSize="small" />,
      title: 'Bold',
      action: () => editor.chain().focus().toggleBold().run(),
      isActive: editor.isActive('bold'),
    },
    {
      icon: <FormatItalicIcon fontSize="small" />,
      title: 'Italic',
      action: () => editor.chain().focus().toggleItalic().run(),
      isActive: editor.isActive('italic'),
    },
    {
      icon: <StrikethroughSIcon fontSize="small" />,
      title: 'Strikethrough',
      action: () => editor.chain().focus().toggleStrike().run(),
      isActive: editor.isActive('strike'),
    },
    { divider: true },
    {
      icon: <FormatListBulletedIcon fontSize="small" />,
      title: 'Bullet List',
      action: () => editor.chain().focus().toggleBulletList().run(),
      isActive: editor.isActive('bulletList'),
    },
    {
      icon: <FormatListNumberedIcon fontSize="small" />,
      title: 'Numbered List',
      action: () => editor.chain().focus().toggleOrderedList().run(),
      isActive: editor.isActive('orderedList'),
    },
    { divider: true },
    {
      icon: <CodeIcon fontSize="small" />,
      title: 'Code',
      action: () => editor.chain().focus().toggleCode().run(),
      isActive: editor.isActive('code'),
    },
    {
      icon: <FormatQuoteIcon fontSize="small" />,
      title: 'Blockquote',
      action: () => editor.chain().focus().toggleBlockquote().run(),
      isActive: editor.isActive('blockquote'),
    },
    { divider: true },
    {
      icon: <UndoIcon fontSize="small" />,
      title: 'Undo',
      action: () => editor.chain().focus().undo().run(),
      isActive: false,
    },
    {
      icon: <RedoIcon fontSize="small" />,
      title: 'Redo',
      action: () => editor.chain().focus().redo().run(),
      isActive: false,
    },
  ];

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 0.3,
        px: 1,
        py: 0.5,
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: 'action.hover',
        borderRadius: '12px 12px 0 0',
      }}
    >
      {buttons.map((btn, i) =>
        btn.divider ? (
          <Divider
            key={i}
            orientation="vertical"
            flexItem
            sx={{ mx: 0.5, my: 0.5 }}
          />
        ) : (
          <Tooltip key={i} title={btn.title} arrow>
            <IconButton
              size="small"
              onClick={btn.action}
              sx={{
                borderRadius: 1.5,
                color: btn.isActive ? 'primary.main' : 'text.secondary',
                bgcolor: btn.isActive
                  ? 'rgba(30, 58, 95, 0.12)'
                  : 'transparent',
                '&:hover': {
                  bgcolor: btn.isActive
                    ? 'rgba(30, 58, 95, 0.18)'
                    : 'action.hover',
                },
              }}
            >
              {btn.icon}
            </IconButton>
          </Tooltip>
        )
      )}
    </Box>
  );
}

/**
 * NewPost page — form for creating a new post with a title, rich text body (Tiptap),
 * and an optional image attachment.
 *
 * Auth guard: redirects unauthenticated users to /login.
 * Waits for the session check to complete before deciding.
 */
function NewPost() {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [uploading, setUploading] = useState(false);
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const editor = useEditor({
    extensions: [StarterKit],
    content: '',
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
      },
    },
  });

  const handleImageSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowed = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!allowed.includes(file.type)) {
      setError('Invalid file type. Use PNG, JPG, GIF, or WebP.');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File too large. Maximum size is 5 MB.');
      return;
    }

    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setError('');
  }, []);

  const removeImage = useCallback(() => {
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImageFile(null);
    setImagePreview('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [imagePreview]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const body = editor?.getHTML() || '';
    const textContent = editor?.getText()?.trim() || '';

    // Validation
    if (!title.trim() || !textContent) {
      setError('Please fill in both the title and content.');
      return;
    }

    setLoading(true);
    try {
      let imageUrl = '';

      // Upload image first if selected
      if (imageFile) {
        setUploading(true);
        const uploadResult = await uploadPostImage(imageFile);
        imageUrl = uploadResult.url;
        setUploading(false);
      }

      await createPost(title, body, imageUrl);
      navigate('/');
    } catch (err) {
      setError(err.message);
      setUploading(false);
    } finally {
      setLoading(false);
    }
  };

  // Wait for session check to complete before redirecting
  if (authLoading) return null;

  // If not logged in, redirect to the login page
  if (!user) return <Navigate to="/login" replace />;

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', px: 3, py: 6 }}>
      <Card
        sx={{
          width: '100%',
          maxWidth: 700,
          borderRadius: 3,
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.1)',
        }}
      >
        <CardContent sx={{ p: 4 }}>
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

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              sx={{ mb: 2.5 }}
              slotProps={{ inputLabel: { shrink: true } }}
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
              <EditorContent editor={editor} />
            </Box>

            {/* Image Upload */}
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
              onChange={handleImageSelect}
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
                  onClick={removeImage}
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

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
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
                ? 'Uploading image...'
                : loading
                  ? 'Publishing...'
                  : 'Publish Post'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default NewPost;
