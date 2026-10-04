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
import { timeAgo } from '../../utils/timeAgo';

const actionSx = { textTransform: 'none', fontWeight: 600, whiteSpace: 'nowrap' };

/** Turn the post's HTML body into a short plain-text preview. */
function preview(html, length = 120) {
  const text = new DOMParser().parseFromString(html || '', 'text/html').body.textContent || '';
  return text.length > length ? `${text.slice(0, length)}…` : text;
}

/** Reported post: title, body preview, and author link. */
function PostInfo({ report }) {
  return (
    <>
      <Typography variant="body2" sx={{ fontWeight: 700 }}>{report.post_title}</Typography>
      <Typography variant="caption" color="text.secondary" component="div">
        {preview(report.post_body)}
      </Typography>
      <Typography variant="caption">
        by <Link to={`/profile/${report.author_id}`}>{report.author_name}</Link>
        {report.author_is_banned ? ' (banned)' : ''}
      </Typography>
    </>
  );
}

/** Delete post / Ban author / Dismiss buttons. */
function ReportButtons({ report, currentUserId, onDelete, onBan, onDismiss }) {
  return (
    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
      <Button size="small" color="error" variant="contained" sx={actionSx}
        onClick={() => onDelete(report)}>
        Delete post
      </Button>
      <Button size="small" color="error" variant="outlined" sx={actionSx}
        disabled={Boolean(report.author_is_banned) || report.author_id === currentUserId}
        onClick={() => onBan(report)}>
        Ban author
      </Button>
      <Button size="small" sx={actionSx} onClick={() => onDismiss(report)}>
        Dismiss
      </Button>
    </Box>
  );
}

/**
 * AdminReports — pending reports with moderator actions.
 * Phones: one card per report (buttons always visible).
 * Larger screens: a table.
 *
 * @param {Object}   props
 * @param {Array}    props.reports       - Pending reports.
 * @param {number}   props.currentUserId - The logged-in admin (can't ban themselves).
 * @param {boolean}  props.isPhone       - Render cards instead of a table.
 * @param {Function} props.onDelete      - Delete the reported post.
 * @param {Function} props.onBan         - Ban the post's author.
 * @param {Function} props.onDismiss     - Dismiss the report.
 */
function AdminReports({ reports, currentUserId, isPhone, onDelete, onBan, onDismiss }) {
  const buttonProps = { currentUserId, onDelete, onBan, onDismiss };

  if (reports.length === 0) {
    return (
      <Paper sx={{ borderRadius: 3, py: 4, textAlign: 'center', color: 'text.secondary' }}>
        No pending reports 🎉
      </Paper>
    );
  }

  if (isPhone) {
    return reports.map((report) => (
      <Paper key={report.id} sx={{ borderRadius: 3, p: 2, mb: 1.5 }}>
        <PostInfo report={report} />
        <Typography variant="body2" sx={{ mt: 1, overflowWrap: 'anywhere' }}>
          <strong>Reason:</strong> {report.reason}
        </Typography>
        <Typography variant="caption" color="text.secondary" component="div" sx={{ mb: 1.5 }}>
          Reported by {report.reporter_name} · {timeAgo(report.created_at)}
        </Typography>
        <ReportButtons report={report} {...buttonProps} />
      </Paper>
    ));
  }

  return (
    <TableContainer component={Paper} sx={{ borderRadius: 3 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 700 }}>Post</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>Reason</TableCell>
            <TableCell sx={{ fontWeight: 700 }}>Reported by</TableCell>
            <TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {reports.map((report) => (
            <TableRow key={report.id}>
              <TableCell sx={{ maxWidth: 320 }}>
                <PostInfo report={report} />
              </TableCell>
              <TableCell sx={{ maxWidth: 240, overflowWrap: 'anywhere' }}>{report.reason}</TableCell>
              <TableCell>
                <Typography variant="body2">{report.reporter_name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {timeAgo(report.created_at)}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <ReportButtons report={report} {...buttonProps} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default AdminReports;
