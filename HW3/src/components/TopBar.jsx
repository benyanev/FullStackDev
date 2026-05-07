import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import ForumRoundedIcon from '@mui/icons-material/ForumRounded';

function TopBar() {
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
          variant="h6"
          sx={{
            flexGrow: 1,
            fontWeight: 700,
            letterSpacing: '0.5px',
          }}
        >
          SocialApp
        </Typography>

        {/* Menu buttons — right side */}
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {['Home', 'Users', 'About', 'Login'].map((label) => (
            <Button
              key={label}
              color="inherit"
              sx={{
                borderRadius: 2,
                px: 2,
                textTransform: 'none',
                fontWeight: 500,
                transition: 'background 0.25s',
                '&:hover': {
                  background: 'rgba(255, 255, 255, 0.12)',
                },
              }}
            >
              {label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default TopBar;
