import { Link } from 'react-router-dom';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';

const actionSx = { textTransform: 'none', fontWeight: 600, whiteSpace: 'nowrap' };

/** Name (linked to the profile) and email. */
function UserInfo({ user }) {
  return (
    <>
      <Typography component={Link} to={`/profile/${user.id}`} variant="body2"
        sx={{ fontWeight: 600, color: 'text.primary' }}>
        {user.name}
      </Typography>
      <Typography variant="caption" color="text.secondary" component="div"
        sx={{ overflowWrap: 'anywhere' }}>
        {user.email}
      </Typography>
    </>
  );
}

/** Moderator / Bot / Banned chips. */
function UserChips({ user }) {
  return (
    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
      {user.role === 'admin' && <Chip label="Moderator" size="small" color="primary" />}
      {Boolean(user.is_agent) && <Chip label="Bot" size="small" color="secondary" variant="outlined" />}
      {Boolean(user.is_banned) && <Chip label="Banned" size="small" color="error" />}
    </Box>
  );
}

/** Make/Remove moderator and Ban/Unban buttons ("You" for the admin themselves). */
function UserButtons({ user, isSelf, onToggleRole, onToggleBan }) {
  if (isSelf) {
    return <Typography variant="caption" color="text.secondary">You</Typography>;
  }
  return (
    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
      <Button size="small" sx={actionSx} onClick={() => onToggleRole(user)}>
        {user.role === 'admin' ? 'Remove moderator' : 'Make moderator'}
      </Button>
      <Button size="small" color="error" variant={user.is_banned ? 'outlined' : 'text'}
        sx={actionSx} onClick={() => onToggleBan(user)}>
        {user.is_banned ? 'Unban' : 'Ban'}
      </Button>
    </Box>
  );
}

/**
 * AdminUsers — every user with role/ban status and moderator actions.
 * Phones: one card per user. Larger screens: a table.
 *
 * @param {Object}   props
 * @param {Array}    props.users         - Users with role, is_banned, is_agent.
 * @param {number}   props.currentUserId - The logged-in admin.
 * @param {boolean}  props.isPhone       - Render cards instead of a table.
 * @param {Function} props.onToggleRole  - Promote / demote a moderator.
 * @param {Function} props.onToggleBan   - Ban / unban a user.
 */
function AdminUsers({ users, currentUserId, isPhone, onToggleRole, onToggleBan }) {
  const buttonProps = { onToggleRole, onToggleBan };

  if (isPhone) {
    return users.map((u) => (
      <Paper key={u.id} sx={{ borderRadius: 3, p: 2, mb: 1.5 }}>
        <UserInfo user={u} />
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1, mt: 1 }}>
          <UserChips user={u} />
          <UserButtons user={u} isSelf={u.id === currentUserId} {...buttonProps} />
        </Box>
      </Paper>
    ));
  }

  return (
    <TableContainer component={Paper} sx={{ borderRadius: 3 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 700 }}>User</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
            <TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {users.map((u) => (
            <TableRow key={u.id}>
              <TableCell><UserInfo user={u} /></TableCell>
              <TableCell><UserChips user={u} /></TableCell>
              <TableCell align="right">
                <UserButtons user={u} isSelf={u.id === currentUserId} {...buttonProps} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default AdminUsers;
