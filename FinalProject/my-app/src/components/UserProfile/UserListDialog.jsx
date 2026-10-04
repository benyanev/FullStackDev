import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import CloseIcon from '@mui/icons-material/Close';
import { getAvatarColor } from '../../utils/avatarColor';

/**
 * UserListDialog — reusable dialog that displays a list of users (followers or following).
 * Replaces the two nearly-identical dialogs in the original UserProfile.
 *
 * @param {Object}   props
 * @param {boolean}  props.open          - Whether the dialog is open.
 * @param {function} props.onClose       - Handler to close the dialog.
 * @param {string}   props.title         - Dialog title (e.g. "Followers" or "Following").
 * @param {Array}    props.users         - Array of user objects to display.
 * @param {string}   props.emptyMessage  - Message to show when the list is empty.
 */
function UserListDialog({ open, onClose, title, users, emptyMessage }) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', fontWeight: 700 }}>
        {title}
        <IconButton onClick={onClose} aria-label="Close" sx={{ ml: 'auto' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        {users.length === 0 ? (
          <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
            {emptyMessage}
          </Typography>
        ) : (
          <List disablePadding>
            {users.map((u) => (
              <ListItem key={u.id}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: getAvatarColor(u.name), width: 36, height: 36, fontSize: 16 }}>
                    {u.name[0].toUpperCase()}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {u.name}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>
    </Dialog>
  );
}

export default UserListDialog;
