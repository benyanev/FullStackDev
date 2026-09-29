import { useState } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import { useAuth } from '../context/AuthContext';

/**
 * Signup page — name, email, password, and confirm password form.
 * On successful signup, logs the user in and navigates to the home page.
 * Redirects to "/" if the user is already authenticated.
 */
function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const { signup, user } = useAuth();
  const navigate = useNavigate();

  // Already authenticated — skip the signup form and go home
  if (user) return <Navigate to="/" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!name.trim() || !email.trim() || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    try {
      await signup(name, email, password);
      navigate('/');
    } catch (err) {
      setError(err.message);
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
            sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}
          >
            Sign Up
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              sx={{ mb: 2.5 }}
              slotProps={{
                inputLabel: { shrink: true },
                htmlInput: { 'data-testid': 'signup-name' },
              }}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 2.5 }}
              slotProps={{
                inputLabel: { shrink: true },
                htmlInput: { 'data-testid': 'signup-email' },
              }}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 2.5 }}
              slotProps={{
                inputLabel: { shrink: true },
                htmlInput: { 'data-testid': 'signup-password' },
              }}
            />
            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              sx={{ mb: 3 }}
              slotProps={{
                inputLabel: { shrink: true },
                htmlInput: { 'data-testid': 'signup-confirm-password' },
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              data-testid="signup-submit"
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
              Sign Up
            </Button>
          </Box>

          <Typography
            variant="body2"
            sx={{ mt: 2.5, textAlign: 'center', color: 'text.secondary' }}
          >
            Already have an account?{' '}
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

export default Signup;
