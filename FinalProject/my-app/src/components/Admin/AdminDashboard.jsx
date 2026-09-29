import { useState } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../../context/AuthContext';
import { useAdminDashboard } from './useAdminDashboard';
import AdminReports from './AdminReports';
import AdminUsers from './AdminUsers';

/**
 * AdminDashboard — moderator page at /admin.
 * "Reports" tab: pending post reports with Delete post / Ban author / Dismiss.
 * "Users" tab: every user with Make moderator and Ban / Unban.
 *
 * Responsive: on phones both tabs show cards (buttons always visible);
 * on larger screens they show tables.
 */
function AdminDashboard() {
  const { user, loading: authLoading } = useAuth();
  const isAdmin = user?.role === 'admin';
  const [tab, setTab] = useState(0);
  const theme = useTheme();
  const isPhone = useMediaQuery(theme.breakpoints.down('sm'));
  const {
    reports, users, loading, error, dismissReport, deletePost, banAuthor, toggleBan, toggleRole,
  } = useAdminDashboard(isAdmin);

  if (authLoading) return null;

  if (!isAdmin) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', mt: 6, px: { xs: 2, sm: 3 } }}>
        <Alert severity="warning">This page is for moderators only.</Alert>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        // width 100%: inside #root's flex column, mx: 'auto' alone makes the box
        // as wide as its content instead of the screen
        width: '100%',
        maxWidth: 1100,
        mx: 'auto',
        px: { xs: 2, sm: 3 },
        py: { xs: 2.5, sm: 4 },
      }}
    >
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 3, textAlign: 'center' }}>
        Admin Dashboard
      </Typography>

      <Tabs value={tab} onChange={(e, value) => setTab(value)} variant="fullWidth"
        sx={{ mb: 2, maxWidth: 400, mx: 'auto' }}>
        <Tab label={`Reports (${reports.length})`} sx={{ textTransform: 'none', fontWeight: 600 }} />
        <Tab label={`Users (${users.length})`} sx={{ textTransform: 'none', fontWeight: 600 }} />
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : tab === 0 ? (
        <AdminReports
          reports={reports}
          currentUserId={user.id}
          isPhone={isPhone}
          onDelete={deletePost}
          onBan={banAuthor}
          onDismiss={dismissReport}
        />
      ) : (
        <AdminUsers
          users={users}
          currentUserId={user.id}
          isPhone={isPhone}
          onToggleRole={toggleRole}
          onToggleBan={toggleBan}
        />
      )}
    </Box>
  );
}

export default AdminDashboard;
