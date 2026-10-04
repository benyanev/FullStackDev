import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Divider from '@mui/material/Divider';
import FormatBoldIcon from '@mui/icons-material/FormatBold';
import FormatItalicIcon from '@mui/icons-material/FormatItalic';
import StrikethroughSIcon from '@mui/icons-material/StrikethroughS';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import CodeIcon from '@mui/icons-material/Code';
import FormatQuoteIcon from '@mui/icons-material/FormatQuote';
import InsertLinkIcon from '@mui/icons-material/InsertLink';
import UndoIcon from '@mui/icons-material/Undo';
import RedoIcon from '@mui/icons-material/Redo';

/**
 * MenuBar — toolbar for the Tiptap rich text editor.
 * Provides formatting buttons for bold, italic, hyperlinks, lists, code, blockquote, etc.
 *
 * @param {Object} props
 * @param {Object} props.editor - Tiptap editor instance.
 */
function MenuBar({ editor }) {
  if (!editor) return null;

  // Hyperlink: ask for a URL (empty = remove the link). Tiptap's Link extension
  // only accepts safe protocols (http/https/mailto...), never javascript:.
  const setLink = () => {
    const previous = editor.getAttributes('link').href || '';
    const url = window.prompt('Link URL (leave empty to remove the link):', previous);
    if (url === null) return; // cancelled

    const chain = editor.chain().focus().extendMarkRange('link');
    if (url.trim() === '') {
      chain.unsetLink().run();
    } else {
      chain.setLink({ href: url.trim() }).run();
    }
  };

  const buttons = [
    {
      icon: <FormatBoldIcon fontSize="small" />,
      title: 'Bold',
      action: () => editor.chain().focus().toggleBold().run(),
      isActive: editor.isActive('bold'),
    },
    {
      icon: <FormatItalicIcon fontSize="small" />,
      title: 'Italic',
      action: () => editor.chain().focus().toggleItalic().run(),
      isActive: editor.isActive('italic'),
    },
    {
      icon: <StrikethroughSIcon fontSize="small" />,
      title: 'Strikethrough',
      action: () => editor.chain().focus().toggleStrike().run(),
      isActive: editor.isActive('strike'),
    },
    {
      icon: <InsertLinkIcon fontSize="small" />,
      title: 'Link',
      action: setLink,
      isActive: editor.isActive('link'),
    },
    { divider: true },
    {
      icon: <FormatListBulletedIcon fontSize="small" />,
      title: 'Bullet List',
      action: () => editor.chain().focus().toggleBulletList().run(),
      isActive: editor.isActive('bulletList'),
    },
    {
      icon: <FormatListNumberedIcon fontSize="small" />,
      title: 'Numbered List',
      action: () => editor.chain().focus().toggleOrderedList().run(),
      isActive: editor.isActive('orderedList'),
    },
    { divider: true },
    {
      icon: <CodeIcon fontSize="small" />,
      title: 'Code',
      action: () => editor.chain().focus().toggleCode().run(),
      isActive: editor.isActive('code'),
    },
    {
      icon: <FormatQuoteIcon fontSize="small" />,
      title: 'Blockquote',
      action: () => editor.chain().focus().toggleBlockquote().run(),
      isActive: editor.isActive('blockquote'),
    },
    { divider: true },
    {
      icon: <UndoIcon fontSize="small" />,
      title: 'Undo',
      action: () => editor.chain().focus().undo().run(),
      isActive: false,
    },
    {
      icon: <RedoIcon fontSize="small" />,
      title: 'Redo',
      action: () => editor.chain().focus().redo().run(),
      isActive: false,
    },
  ];

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 0.3,
        px: 1,
        py: 0.5,
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: 'action.hover',
        borderRadius: '12px 12px 0 0',
      }}
    >
      {buttons.map((btn, i) =>
        btn.divider ? (
          <Divider
            key={i}
            orientation="vertical"
            flexItem
            sx={{ mx: 0.5, my: 0.5 }}
          />
        ) : (
          <Tooltip key={i} title={btn.title} arrow>
            <IconButton
              size="small"
              aria-label={btn.title}
              onClick={btn.action}
              sx={{
                borderRadius: 1.5,
                color: btn.isActive ? 'primary.main' : 'text.secondary',
                bgcolor: btn.isActive
                  ? 'rgba(30, 58, 95, 0.12)'
                  : 'transparent',
                '&:hover': {
                  bgcolor: btn.isActive
                    ? 'rgba(30, 58, 95, 0.18)'
                    : 'action.hover',
                },
              }}
            >
              {btn.icon}
            </IconButton>
          </Tooltip>
        ),
      )}
    </Box>
  );
}

export default MenuBar;
