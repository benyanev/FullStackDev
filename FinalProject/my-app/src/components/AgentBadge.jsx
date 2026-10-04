import Chip from '@mui/material/Chip';
import Tooltip from '@mui/material/Tooltip';
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined';

/**
 * AgentBadge — small "Bot" chip shown next to the name of an AI agent account,
 * so users always know when they are talking to a bot.
 *
 * @param {Object} props
 * @param {string} [props.personality] - Shown as a tooltip when provided.
 */
function AgentBadge({ personality }) {
  const chip = (
    <Chip
      icon={<SmartToyOutlinedIcon />}
      label="Bot"
      size="small"
      color="secondary"
      variant="outlined"
      sx={{ height: 20, fontSize: 11, fontWeight: 600, '& .MuiChip-icon': { fontSize: 14 } }}
    />
  );

  return personality ? <Tooltip title={personality}>{chip}</Tooltip> : chip;
}

export default AgentBadge;
