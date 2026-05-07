import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import { useAuth } from '../context/AuthContext';
import { createPost } from '../services/api';

/**
 * NewPost page — form for creating a new post with title and body.
 * Sends the post to the Flask backend with JWT authentication.
 */
function NewPost() {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, token } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!title.trim() || !body.trim()) {
      setError('Please fill in both the title and content.');
      return;
    }

    setLoading(true);
    try {
      await createPost(title, body, token);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // If not logged in, show a message
  if (!user) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', px: 3, py: 6 }}>
        <Typography variant="h6" color="text.secondary">
          Please log in to create a post.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', px: 3, py: 6 }}>
      <Card
        sx={{
          width: '100%',
          maxWidth: 600,
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
            <TextField
              fullWidth
              label="Content"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              multiline
              rows={6}
              sx={{ mb: 3 }}
              slotProps={{ inputLabel: { shrink: true } }}
            />
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
                  background: 'linear-gradient(135deg, #24476f 0%, #371f7d 100%)',
                },
              }}
            >
              {loading ? 'Publishing...' : 'Publish Post'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default NewPost;
