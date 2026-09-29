import { useState } from 'react';
import { Link } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import { requestPasswordReset } from '../services/reset.service';

/**
 * ResetRequest — "Forgot password?" page.
 * User enters their email and receives a reset link.
 */
function ResetRequest() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!email.trim()) {
      setError('Please enter your email address.');
      return;
    }

    setLoading(true);
    try {
      const data = await requestPasswordReset(email.trim().toLowerCase());
      setMessage(data.message);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', px: { xs: 2, sm: 3 }, py: { xs: 3, sm: 6 } }}>
      <Card
        sx={{
          width: '100%',
          maxWidth: 440,
          borderRadius: 3,
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.1)',
        }}
      >
        <CardContent sx={{ p: { xs: 2.5, sm: 4 } }}>
          <Typography
            variant="h5"
            sx={{ fontWeight: 700, mb: 1, textAlign: 'center' }}
          >
            Reset Password
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 3, textAlign: 'center' }}
          >
            Enter your email address and we'll send you a link to reset your password.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}
          {message && (
            <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
              {message}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              id="reset-email"
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 3 }}
              slotProps={{
                inputLabel: { shrink: true },
              }}
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
              {loading ? 'Sending…' : 'Send Reset Link'}
            </Button>
          </Box>

          <Typography
            variant="body2"
            sx={{ mt: 2.5, textAlign: 'center', color: 'text.secondary' }}
          >
            Remember your password?{' '}
            <Typography
              component={Link}
              to="/login"
              variant="body2"
              sx={{ fontWeight: 600, color: 'primary.main', textDecoration: 'none' }}
            >
              Log In
            </Typography>
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

export default ResetRequest;
