import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import ForumRoundedIcon from '@mui/icons-material/ForumRounded';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import MobileMenu from './MobileMenu';

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
 * - Admins also get an "Admin" link to the Admin Dashboard
 *
 * Responsive: below the `md` breakpoint the button row is replaced by a
 * hamburger menu (MobileMenu); the "+ New Post" button stays visible.
 */
function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  let menuItems = user ? authMenuItems : guestMenuItems;
  if (user?.role === 'admin') {
    menuItems = [...menuItems, { label: 'Admin', to: '/admin' }];
  }

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
        <ForumRoundedIcon sx={{ mr: 1.5, fontSize: 28, display: { xs: 'none', sm: 'block' } }} />
        <Typography
          component={Link}
          to="/"
          variant="h6"
          sx={{
            fontWeight: 700,
            letterSpacing: '0.5px',
            color: 'inherit',
            textDecoration: 'none',
            mr: { xs: 1, sm: 2 },
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

        {/* Menu buttons — right side (desktop / tablet only) */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 0.5, alignItems: 'center' }}>
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
                component={Link}
                to={`/profile/${user.id}`}
                variant="body2"
                sx={{
                  ml: 1,
                  px: 1.5,
                  py: 0.5,
                  borderRadius: 2,
                  background: 'rgba(255, 255, 255, 0.1)',
                  fontWeight: 600,
                  color: 'inherit',
                  textDecoration: 'none',
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.2)',
                  },
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

        {/* Hamburger menu — phones and small tablets */}
        <MobileMenu
          menuItems={menuItems}
          user={user}
          pathname={location.pathname}
          onLogout={handleLogout}
        />
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;
