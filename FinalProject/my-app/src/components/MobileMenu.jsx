import { useState } from 'react';
import { Link } from 'react-router-dom';
import IconButton from '@mui/material/IconButton';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import MenuIcon from '@mui/icons-material/Menu';

/**
 * MobileMenu — hamburger button + slide-in drawer used by TopBar on small
 * screens (below the `md` breakpoint), where the full button row doesn't fit.
 *
 * @param {Object}   props
 * @param {Array}    props.menuItems - `{ label, to }` links (same list as the desktop bar).
 * @param {Object}   props.user      - Logged-in user, or null.
 * @param {string}   props.pathname  - Current route, to highlight the active link.
 * @param {Function} props.onLogout  - Logout handler.
 */
function MobileMenu({ menuItems, user, pathname, onLogout }) {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return (
    <>
      <IconButton
        color="inherit"
        aria-label="Open menu"
        onClick={() => setOpen(true)}
        sx={{ display: { xs: 'inline-flex', md: 'none' } }}
      >
        <MenuIcon />
      </IconButton>

      <Drawer anchor="right" open={open} onClose={close}>
        <Box sx={{ width: 240 }} role="navigation">
          {user && (
            <>
              <Box sx={{ px: 2, py: 2 }}>
                <Typography variant="caption" color="text.secondary">Signed in as</Typography>
                <Typography sx={{ fontWeight: 700 }}>{user.name}</Typography>
              </Box>
              <Divider />
            </>
          )}

          <List>
            {menuItems.filter((item) => item.to).map(({ label, to }) => (
              <ListItemButton
                key={label}
                component={Link}
                to={to}
                selected={pathname === to}
                onClick={close}
              >
                <ListItemText primary={label} />
              </ListItemButton>
            ))}

            {user && (
              <>
                <ListItemButton component={Link} to="/new-post" onClick={close}>
                  <ListItemText primary="+ New Post" />
                </ListItemButton>
                <ListItemButton component={Link} to={`/profile/${user.id}`} onClick={close}>
                  <ListItemText primary="My Profile" />
                </ListItemButton>
                <Divider sx={{ my: 1 }} />
                <ListItemButton
                  onClick={() => {
                    close();
                    onLogout();
                  }}
                >
                  <ListItemText primary="Logout" />
                </ListItemButton>
              </>
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
}

export default MobileMenu;
