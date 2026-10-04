import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import { confirmPasswordReset } from '../services/reset.service';

/**
 * ResetConfirm — "Set new password" page.
 * Accessed via the reset link in the email: /reset-password?token=...
 * User enters a new password which replaces the old one.
 */
function ResetConfirm() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!password.trim() || !confirmPw.trim()) {
      setError('Please fill in both fields.');
      return;
    }
    if (password !== confirmPw) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (!token) {
      setError('Invalid reset link. Please request a new one.');
      return;
    }

    setLoading(true);
    try {
      const data = await confirmPasswordReset(token, password);
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
            Set New Password
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 3, textAlign: 'center' }}
          >
            Enter your new password below.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}
          {message && (
            <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>
              {message}{' '}
              <Typography
                component={Link}
                to="/login"
                variant="body2"
                sx={{ fontWeight: 600, color: 'inherit' }}
              >
                Log in now →
              </Typography>
            </Alert>
          )}

          {!message && (
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                id="reset-new-password"
                fullWidth
                label="New Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={{ mb: 2.5 }}
                slotProps={{
                  inputLabel: { shrink: true },
                }}
              />
              <TextField
                id="reset-confirm-password"
                fullWidth
                label="Confirm Password"
                type="password"
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
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
                {loading ? 'Resetting…' : 'Reset Password'}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default ResetConfirm;
