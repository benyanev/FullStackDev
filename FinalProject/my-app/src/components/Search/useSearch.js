import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchUsers } from '../../services/users.service';

/**
 * Custom hook for the Search autocomplete component.
 * Fetches all users on mount, filters locally by name prefix,
 * and handles click-outside-to-close behavior.
 *
 * @returns {{
 *   query: string,
 *   setQuery: function,
 *   results: Array,
 *   open: boolean,
 *   setOpen: function,
 *   containerRef: React.RefObject,
 *   handleSelect: (user: Object) => void,
 * }}
 */
export function useSearch() {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [allUsers, setAllUsers] = useState([]);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  // Fetch all users once on mount so we can filter locally in real time
  useEffect(() => {
    fetchUsers(0, 100).then((users) => {
      setAllUsers(users);
    });
  }, []);

  // Filter locally: show only names that START with the typed text (Derived State)
  const lowerQuery = query.toLowerCase().trim();
  const results = lowerQuery
    ? allUsers.filter((user) => user.name.toLowerCase().startsWith(lowerQuery))
    : [];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle user selection — navigate to their profile
  const handleSelect = (user) => {
    setQuery('');
    setOpen(false);
    navigate(`/profile/${user.id}`);
  };

  return { query, setQuery, results, open, setOpen, containerRef, handleSelect };
}
