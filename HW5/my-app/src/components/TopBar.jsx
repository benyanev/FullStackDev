import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import ForumRoundedIcon from '@mui/icons-material/ForumRounded';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Menu items for unauthenticated users
const guestMenuItems = [
  { label: 'Home', to: '/' },
  { label: 'Users', to: '/users' },
  { label: 'About', to: null },
  { label: 'Login', to: '/login' },
];

// Menu items for authenticated users (Login replaced by user info)
const authMenuItems = [
  { label: 'Home', to: '/' },
  { label: 'Users', to: '/users' },
  { label: 'About', to: null },
];

/**
 * TopBar — sticky navigation bar at the top of every page.
 *
 * Renders different menu items based on authentication state:
 * - Logged out: Home, Users, About, Login
 * - Logged in:  Home, Users, About, + New Post, user name badge, Logout
 */
function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const menuItems = user ? authMenuItems : guestMenuItems;

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background: 'linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      <Toolbar>
        {/* App name — left side */}
        <ForumRoundedIcon sx={{ mr: 1.5, fontSize: 28 }} />
        <Typography
          component={Link}
          to="/"
          variant="h6"
          sx={{
            fontWeight: 700,
            letterSpacing: '0.5px',
            color: 'inherit',
            textDecoration: 'none',
            mr: 2,
          }}
        >
          SocialApp
        </Typography>

        {/* New Post button — only visible when logged in */}
        {user && (
          <Button
            component={Link}
            to="/new-post"
            color="inherit"
            variant="outlined"
            size="small"
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              borderColor: 'rgba(255, 255, 255, 0.4)',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.8)',
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            + New Post
          </Button>
        )}

        {/* Spacer to push menu buttons to the right */}
        <Box sx={{ flexGrow: 1 }} />

        {/* Menu buttons — right side */}
        <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
          {menuItems.map(({ label, to }) => {
            const isActive = to && location.pathname === to;
            const buttonProps = to ? { component: Link, to } : {};

            return (
              <Button
                key={label}
                color="inherit"
                {...buttonProps}
                sx={{
                  borderRadius: 2,
                  px: 2,
                  textTransform: 'none',
                  fontWeight: isActive ? 700 : 500,
                  transition: 'background 0.25s',
                  background: isActive
                    ? 'rgba(255, 255, 255, 0.12)'
                    : 'transparent',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.12)',
                  },
                }}
              >
                {label}
              </Button>
            );
          })}

          {/* Logged-in: show user name + Logout */}
          {user && (
            <>
              <Typography
                variant="body2"
                sx={{
                  ml: 1,
                  px: 1.5,
                  py: 0.5,
                  borderRadius: 2,
                  background: 'rgba(255, 255, 255, 0.1)',
                  fontWeight: 600,
                }}
              >
                {user.name}
              </Typography>
              <Button
                color="inherit"
                onClick={handleLogout}
                sx={{
                  borderRadius: 2,
                  px: 2,
                  textTransform: 'none',
                  fontWeight: 500,
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.12)',
                  },
                }}
              >
                Logout
              </Button>
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;
