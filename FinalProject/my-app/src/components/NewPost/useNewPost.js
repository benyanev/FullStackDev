import { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { useAuth } from '../../context/AuthContext';
import { createPost } from '../../services/posts.service';
import { uploadPostImage, uploadPostVideo } from '../../services/upload.service';

const IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
const VIDEO_TYPES = ['video/mp4', 'video/webm'];
const MAX_IMAGE_SIZE = 5 * 1024 * 1024;   // 5 MB
const MAX_VIDEO_SIZE = 50 * 1024 * 1024;  // 50 MB

/**
 * Custom hook for the NewPost form.
 * Manages title, Tiptap editor, media (image OR video) selection/validation/removal,
 * and form submission (upload media → create post → navigate).
 *
 * @returns {{
 *   title: string,
 *   setTitle: function,
 *   error: string,
 *   loading: boolean,
 *   uploading: boolean,
 *   mediaPreview: string,
 *   mediaType: 'image'|'video'|'',
 *   fileInputRef: React.RefObject,
 *   editor: Object,
 *   user: Object|null,
 *   authLoading: boolean,
 *   handleMediaSelect: (e: Event) => void,
 *   removeMedia: () => void,
 *   handleSubmit: (e: Event) => Promise<void>,
 *   moderationMessage: string,
 *   closeModerationDialog: () => void,
 * }}
 */
export function useNewPost() {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [mediaFile, setMediaFile] = useState(null);
  const [mediaPreview, setMediaPreview] = useState('');
  const [mediaType, setMediaType] = useState(''); // 'image' | 'video' | ''
  const [uploading, setUploading] = useState(false);
  const [moderationMessage, setModerationMessage] = useState('');
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const editor = useEditor({
    extensions: [
      // StarterKit includes bold, italic, lists, and Link (hyperlinks).
      // Links open with https:// when typed without a protocol, and don't
      // navigate away while editing.
      StarterKit.configure({ link: { openOnClick: false, defaultProtocol: 'https' } }),
    ],
    content: '',
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
      },
    },
  });

  const handleMediaSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type — one image OR one video
    const isVideo = VIDEO_TYPES.includes(file.type);
    if (!isVideo && !IMAGE_TYPES.includes(file.type)) {
      setError('Invalid file type. Use PNG, JPG, GIF, WebP, MP4, or WebM.');
      return;
    }

    // Validate file size (5 MB images, 50 MB videos)
    const maxSize = isVideo ? MAX_VIDEO_SIZE : MAX_IMAGE_SIZE;
    if (file.size > maxSize) {
      setError(`File too large. Maximum size is ${maxSize / (1024 * 1024)} MB.`);
      return;
    }

    setMediaFile(file);
    setMediaType(isVideo ? 'video' : 'image');
    setMediaPreview(URL.createObjectURL(file));
    setError('');
  }, []);

  // Free the preview's memory when it is replaced or the page is left
  useEffect(() => () => {
    if (mediaPreview) URL.revokeObjectURL(mediaPreview);
  }, [mediaPreview]);

  const removeMedia = useCallback(() => {
    setMediaFile(null);
    setMediaType('');
    setMediaPreview('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const body = editor?.getHTML() || '';
    const textContent = editor?.getText()?.trim() || '';

    // Validation
    if (!title.trim() || !textContent) {
      setError('Please fill in both the title and content.');
      return;
    }

    setLoading(true);
    try {
      let imageUrl = '';
      let videoUrl = '';

      // Upload the image or video first if one was selected
      if (mediaFile) {
        setUploading(true);
        if (mediaType === 'video') {
          videoUrl = (await uploadPostVideo(mediaFile)).url;
        } else {
          imageUrl = (await uploadPostImage(mediaFile)).url;
        }
        setUploading(false);
      }

      await createPost(title, body, imageUrl, videoUrl);
      navigate('/');
    } catch (err) {
      // 422 = blocked as toxic: explain in a dialog, keep the draft for editing
      if (err.status === 422) {
        setModerationMessage(err.message);
      } else {
        setError(err.message);
      }
      setUploading(false);
    } finally {
      setLoading(false);
    }
  };

  return {
    title,
    setTitle,
    error,
    loading,
    uploading,
    mediaPreview,
    mediaType,
    fileInputRef,
    editor,
    user,
    authLoading,
    handleMediaSelect,
    removeMedia,
    handleSubmit,
    moderationMessage,
    closeModerationDialog: () => setModerationMessage(''),
  };
}
