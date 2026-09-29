import { useState, useEffect, useCallback } from 'react';
import {
  fetchReports,
  updateReport,
  deletePostAsAdmin,
  fetchAdminUsers,
  setUserBanned,
  setUserRole,
} from '../../services/admin.service';

/** Fetch both dashboard lists in parallel. */
async function fetchDashboard() {
  const [reports, users] = await Promise.all([fetchReports(), fetchAdminUsers()]);
  return { reports, users };
}

/**
 * Custom hook for the Admin Dashboard.
 * Loads pending reports and users, and exposes the moderator actions.
 * Every action reloads both lists so the tables always match the server.
 *
 * @param {boolean} isAdmin - Only fetch when the current user is an admin.
 * @returns {{
 *   reports: Array, users: Array, loading: boolean, error: string,
 *   dismissReport: (report: Object) => Promise<void>,
 *   deletePost: (report: Object) => Promise<void>,
 *   banAuthor: (report: Object) => Promise<void>,
 *   toggleBan: (user: Object) => Promise<void>,
 *   toggleRole: (user: Object) => Promise<void>,
 * }}
 */
export function useAdminDashboard(isAdmin) {
  const [reports, setReports] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const applyData = useCallback((data) => {
    setReports(data.reports);
    setUsers(data.users);
  }, []);

  // Initial load
  useEffect(() => {
    if (!isAdmin) return;
    fetchDashboard()
      .then(applyData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [isAdmin, applyData]);

  /** Run an admin action, then refresh the lists (or show the error). */
  const run = async (action) => {
    setError('');
    try {
      await action();
    } catch (err) {
      setError(err.message);
    }
    try {
      applyData(await fetchDashboard());
    } catch (err) {
      setError(err.message);
    }
  };

  const dismissReport = (report) => run(() => updateReport(report.id, 'dismissed'));

  // Deleting the post also deletes all of its reports (ON DELETE CASCADE)
  const deletePost = (report) => run(() => deletePostAsAdmin(report.post_id));

  const banAuthor = (report) => run(async () => {
    await setUserBanned(report.author_id, true);
    await updateReport(report.id, 'resolved');
  });

  const toggleBan = (user) => run(() => setUserBanned(user.id, !user.is_banned));

  const toggleRole = (user) => run(() => setUserRole(user.id, user.role === 'admin' ? 'user' : 'admin'));

  return { reports, users, loading, error, dismissReport, deletePost, banAuthor, toggleBan, toggleRole };
}
