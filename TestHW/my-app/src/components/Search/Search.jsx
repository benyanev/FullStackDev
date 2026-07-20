import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import SearchIcon from '@mui/icons-material/Search';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { getAvatarColor } from '../../utils/avatarColor';
import { useSearch } from './useSearch';

/**
 * Autocomplete-style search input.
 * As the user types, a dropdown appears below with matching users (filtered by name).
 * Selecting a user navigates to their profile page.
 */
function Search() {
  const { query, setQuery, results, open, setOpen, containerRef, handleSelect } = useSearch();

  return (
    <Box ref={containerRef} sx={{ position: 'relative', maxWidth: 500, mx: 'auto', mb: 3 }}>
      <TextField
        fullWidth
        variant="outlined"
        placeholder="Search users by name..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            transition: 'box-shadow 0.25s',
            '&:hover': {
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
            },
            '&.Mui-focused': {
              boxShadow: '0 4px 14px rgba(0, 0, 0, 0.1)',
            },
          },
        }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          },
        }}
      />

      {/* Dropdown results */}
      {open && (
        <Paper
          elevation={6}
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 0.5,
            zIndex: 10,
            maxHeight: 300,
            overflow: 'auto',
            borderRadius: 2,
          }}
        >
          <List disablePadding>
            {results.map((user) => (
              <ListItemButton key={user.id} onClick={() => handleSelect(user)}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: getAvatarColor(user.name), width: 36, height: 36, fontSize: 16 }}>
                    {user.name[0].toUpperCase()}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {user.name}
                    </Typography>
                  }
                  secondary={user.email}
                />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}

export default Search;
